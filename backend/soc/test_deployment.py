import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

from django.db import OperationalError
from django.test import SimpleTestCase
from rest_framework.test import APITestCase


BACKEND = Path(__file__).resolve().parent.parent


class DeploymentSettingsTests(SimpleTestCase):
    def load_settings(self, **overrides):
        env = os.environ.copy()
        for key in ('DATABASE_URL', 'DEBUG', 'RENDER', 'DJANGO_SECRET_KEY'):
            env.pop(key, None)
        env.update(overrides)
        return subprocess.run(
            [sys.executable, '-c',
             'from config.settings import DATABASES, DEBUG; '
             'db = DATABASES["default"]; '
             'print(DEBUG, db["ENGINE"], db.get("CONN_HEALTH_CHECKS"), '
             'db.get("OPTIONS", {}).get("sslmode"))'],
            cwd=BACKEND, env=env, capture_output=True, text=True,
        )

    def test_development_keeps_sqlite(self):
        result = self.load_settings(DEBUG='true')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('True django.db.backends.sqlite3 True', result.stdout)

    def test_production_requires_database_url(self):
        result = self.load_settings(DEBUG='false', DJANGO_SECRET_KEY='test-only-settings-key')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Set DATABASE_URL', result.stderr)

    def test_production_rejects_sqlite(self):
        result = self.load_settings(
            DEBUG='false', DJANGO_SECRET_KEY='test-only-settings-key',
            DATABASE_URL='sqlite:///:memory:',
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Production requires a PostgreSQL', result.stderr)

    def test_render_defaults_to_production_and_preserves_postgres_ssl_option(self):
        for scheme in ('postgres', 'postgresql'):
            with self.subTest(scheme=scheme):
                result = self.load_settings(
                    RENDER='true', DJANGO_SECRET_KEY='test-only-settings-key',
                    DATABASE_URL=f'{scheme}://localhost/davoski_test?sslmode=require',
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('False django.db.backends.postgresql True require', result.stdout)


class StartupTests(SimpleTestCase):
    def run_startup(self, migration_exit):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            calls = root / 'calls'
            for name, script in {
                'python': '#!/bin/sh\necho "python $*" >> "$STARTUP_CALLS"\nexit "$MIGRATION_EXIT"\n',
                'gunicorn': '#!/bin/sh\necho "gunicorn $*" >> "$STARTUP_CALLS"\n',
            }.items():
                executable = root / name
                executable.write_text(script)
                executable.chmod(0o700)
            env = os.environ.copy()
            env.update(PATH=f'{root}:{env["PATH"]}', STARTUP_CALLS=str(calls),
                       MIGRATION_EXIT=str(migration_exit), PORT='10000')
            result = subprocess.run(
                ['sh', str(BACKEND / 'start.sh')], cwd=root, env=env,
                capture_output=True, text=True,
            )
            return result, calls.read_text().splitlines()

    def test_migrations_complete_before_gunicorn_starts(self):
        result, calls = self.run_startup(0)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls[0], 'python manage.py migrate --noinput')
        self.assertEqual(len(calls), 2)
        self.assertTrue(calls[1].startswith('gunicorn config.wsgi:application'))
        self.assertIn('--bind 0.0.0.0:10000', calls[1])

    def test_failed_migration_prevents_gunicorn_startup(self):
        result, calls = self.run_startup(1)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(calls, ['python manage.py migrate --noinput'])


class RegistrationFailureLoggingTests(APITestCase):
    def test_database_failure_stays_500_and_logs_without_sensitive_values(self):
        sensitive = 'private@example.test password-value jwt-value database-password'
        with patch('soc.serializers.RegisterSerializer.create',
                   side_effect=OperationalError(sensitive)):
            with self.assertLogs('soc.exceptions', level='ERROR') as logs:
                response = self.client.post('/api/auth/register/', {
                    'username': 'registration_test', 'email': 'private@example.test',
                    'password': 'DistinctSecret!482',
                }, format='json')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data['status'], 500)
        output = '\n'.join(logs.output)
        self.assertIn('OperationalError', output)
        self.assertIn('RegisterView', output)
        self.assertIn('frames=', output)
        for value in sensitive.split() + ['DistinctSecret!482', 'registration_test']:
            self.assertNotIn(value, output)
            self.assertNotIn(value, str(response.data))
