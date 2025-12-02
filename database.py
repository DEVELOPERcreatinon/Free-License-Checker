# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Copyright (c) 2025 developercreation


from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

Base = declarative_base()

class LicenseKey(Base):
    __tablename__ = 'license_keys'
    
    id = Column(Integer, primary_key=True)
    key_hash = Column(String(64), unique=True, nullable=False, index=True)
    license_type = Column(String(20), nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    expiration_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    is_used = Column(Boolean, default=False)
    used_date = Column(DateTime, nullable=True)
    client_info = Column(Text, nullable=True)
    activation_count = Column(Integer, default=0)
    max_activations = Column(Integer, default=1)

class ActivationLog(Base):
    __tablename__ = 'activation_logs'
    
    id = Column(Integer, primary_key=True)
    key_hash = Column(String(64), nullable=False, index=True)
    activation_date = Column(DateTime, default=datetime.utcnow)
    client_ip = Column(String(45))
    client_info = Column(Text)
    success = Column(Boolean)
    reason = Column(Text)

class DatabaseManager:
    def __init__(self, config, security_manager):
        self.config = config
        self.security = security_manager
        
        if config['database']['type'] == 'sqlite':
            db_url = f"sqlite:///{config['database']['filename']}"
        else:
            raise ValueError("Only SQLite is supported in this implementation")
            
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables"""
        Base.metadata.create_all(self.engine)
    
    def add_license_key(self, key, license_type, validity_days=None):
        """Add license key to database"""
        if validity_days is None:
            validity_days = self.config['licensing']['default_validity_days']
        
        session = self.Session()
        try:
            key_hash = self.security.hash_key(key)
            expiration_date = datetime.utcnow() + timedelta(days=validity_days)
            
            license_key = LicenseKey(
                key_hash=key_hash,
                license_type=license_type,
                expiration_date=expiration_date
            )
            
            session.add(license_key)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error adding license key: {e}")
            return False
        finally:
            session.close()
    
    def validate_license(self, key, license_type, client_info=None, client_ip=None):
        """Validate license"""
        session = self.Session()
        try:
            # Check key format with prefix
            if not self.security.validate_key_format(key, license_type):
                log_entry = ActivationLog(
                    key_hash="",
                    client_ip=client_ip,
                    client_info=client_info,
                    success=False,
                    reason="Invalid key format or prefix mismatch"
                )
                session.add(log_entry)
                session.commit()
                return False, "Invalid key format or prefix mismatch"
            
            key_hash = self.security.hash_key(key)
            
            license_key = session.query(LicenseKey).filter_by(
                key_hash=key_hash,
                license_type=license_type
            ).first()
            
            log_entry = ActivationLog(
                key_hash=key_hash,
                client_ip=client_ip,
                client_info=client_info,
                success=False
            )
            
            if not license_key:
                log_entry.reason = "Key not found"
                session.add(log_entry)
                session.commit()
                return False, "Invalid license key"
            
            if not license_key.is_active:
                log_entry.reason = "Key is inactive"
                session.add(log_entry)
                session.commit()
                return False, "License key is inactive"
            
            if license_key.is_used and not self.config['licensing']['allow_multiple_activations']:
                log_entry.reason = "Key already used"
                session.add(log_entry)
                session.commit()
                return False, "License key has already been used"
            
            if datetime.utcnow() > license_key.expiration_date:
                log_entry.reason = "Key expired"
                session.add(log_entry)
                session.commit()
                return False, "License key has expired"
            
            if license_key.activation_count >= license_key.max_activations:
                log_entry.reason = "Max activations reached"
                session.add(log_entry)
                session.commit()
                return False, "Maximum activations reached"
            
            # Update usage information
            license_key.is_used = True
            license_key.used_date = datetime.utcnow()
            license_key.activation_count += 1
            if client_info:
                license_key.client_info = client_info
            
            log_entry.success = True
            log_entry.reason = "Success"
            session.add(log_entry)
            session.commit()
            
            return True, "License validated successfully"
            
        except Exception as e:
            session.rollback()
            print(f"Error validating license: {e}")
            return False, "Server error during validation"
        finally:
            session.close()
    
    def get_license_stats(self):
        """Get license statistics"""
        session = self.Session()
        try:
            total_keys = session.query(LicenseKey).count()
            active_keys = session.query(LicenseKey).filter_by(is_active=True).count()
            used_keys = session.query(LicenseKey).filter_by(is_used=True).count()
            expired_keys = session.query(LicenseKey).filter(
                LicenseKey.expiration_date < datetime.utcnow()
            ).count()
            
            return {
                'total_keys': total_keys,
                'active_keys': active_keys,
                'used_keys': used_keys,
                'expired_keys': expired_keys
            }
        finally:
            session.close()