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
            raise ValueError("Только SQLite поддерживается в этой реализации")
            
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Создание таблиц в базе данных"""
        Base.metadata.create_all(self.engine)
    
    def add_license_key(self, key, license_type, validity_days=None):
        """Добавление ключа лицензии в базу данных"""
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
            print(f"Ошибка при добавлении ключа лицензии: {e}")
            return False
        finally:
            session.close()
    
    def validate_license(self, key, license_type, client_info=None, client_ip=None):
        """Проверка валидности лицензии"""
        session = self.Session()
        try:
            # Проверка формата ключа с префиксом
            if not self.security.validate_key_format(key, license_type):
                log_entry = ActivationLog(
                    key_hash="",
                    client_ip=client_ip,
                    client_info=client_info,
                    success=False,
                    reason="Неверный формат ключа или несоответствие префикса"
                )
                session.add(log_entry)
                session.commit()
                return False, "Неверный формат ключа или несоответствие префикса"
            
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
                log_entry.reason = "Ключ не найден"
                session.add(log_entry)
                session.commit()
                return False, "Неверный лицензионный ключ"
            
            if not license_key.is_active:
                log_entry.reason = "Ключ неактивен"
                session.add(log_entry)
                session.commit()
                return False, "Лицензионный ключ неактивен"
            
            if license_key.is_used and not self.config['licensing']['allow_multiple_activations']:
                log_entry.reason = "Ключ уже использован"
                session.add(log_entry)
                session.commit()
                return False, "Лицензионный ключ уже был использован"
            
            if datetime.utcnow() > license_key.expiration_date:
                log_entry.reason = "Ключ истек"
                session.add(log_entry)
                session.commit()
                return False, "Срок действия лицензионного ключа истек"
            
            if license_key.activation_count >= license_key.max_activations:
                log_entry.reason = "Достигнуто максимальное количество активаций"
                session.add(log_entry)
                session.commit()
                return False, "Достигнуто максимальное количество активаций"
            
            # Обновляем информацию об использовании
            license_key.is_used = True
            license_key.used_date = datetime.utcnow()
            license_key.activation_count += 1
            if client_info:
                license_key.client_info = client_info
            
            log_entry.success = True
            log_entry.reason = "Успех"
            session.add(log_entry)
            session.commit()
            
            return True, "Лицензия успешно проверена"
            
        except Exception as e:
            session.rollback()
            print(f"Ошибка при проверке лицензии: {e}")
            return False, "Ошибка сервера при проверке"
        finally:
            session.close()
    
    def get_license_stats(self):
        """Получение статистики по лицензиям"""
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