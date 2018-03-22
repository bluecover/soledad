WITH_ENV = env `[ -n "$$WEB_PORT_5000_TCP_PROTO" ] && echo || cat .env 2>/dev/null | xargs`
GULP := gulp
MYSQL := mysql
MYSQL_OPTS ?= -uroot -psolar
REDIS_OPTS ?= -h localhost -p 6379

COMMANDS = help clean install-deps compile-deps unittest apitest webtest pylint initdb fillup fillup-remote docs docs-force remote-zhiwang remote-firewood list-tables migrate-tables
.PHONY: $(COMMANDS)

help:
	@echo "commands: $(COMMANDS)"

clean:
	@find . -name '*.pyc' -type f -delete
	@find . -name '__pycache__' -type d -delete
	@find . -type d -empty -delete
	@rm -rf build dist htmlcov solar.egg-info screenshots

install-deps:
	@[ -n "$(VIRTUAL_ENV)" ] || (echo 'out of virtualenv'; exit 1)
	@pip install -U pip setuptools
	@pip install --trusted-host=devpi.tuluu.com -r requirements.txt
	@pip install --trusted-host=devpi.tuluu.com -r requirements-dev.txt
	@pip install --trusted-host=devpi.tuluu.com -r requirements-testing.txt
	@npm install

compile-deps:
	@pip-compile --trusted-host=devpi.tuluu.com requirements.in
	@pip-compile --trusted-host=devpi.tuluu.com requirements-dev.in
	@pip-compile --trusted-host=devpi.tuluu.com requirements-testing.in

unittest:
	@$(WITH_ENV) py.test --cov=core.models tests

apitest:
	@$(WITH_ENV) py.test --cov=jupiter.views.api apitests

webtest:
	@$(WITH_ENV) py.test -sv webtests

lint:
	@echo "[lint:py] basic"
	@$(WITH_ENV) flake8 --immediate
	@echo "[lint:py] complexity (warning only)"
	@$(WITH_ENV) flake8 --immediate --max-complexity=24 core jupiter || true

lint-release:
	@echo "[lint:py] basic"
	@$(WITH_ENV) flake8 --immediate
	@echo "[lint:py] finished"

initdb:
	@$(WITH_ENV) python -W ignore -m tests.memdb database/
	redis-cli $(REDIS_OPTS) flushall

fillup:
	@$(WITH_ENV) python -W ignore -m tests.init.add_site
	@$(WITH_ENV) python -W ignore -m tests.init.add_user
	@$(WITH_ENV) python -W ignore -m tests.init.add_channel
	@$(WITH_ENV) python -W ignore -m tests.init.add_coupons
	@$(WITH_ENV) python -W ignore -m tests.init.add_location
	@$(WITH_ENV) python -W ignore -m tests.init.add_salary
	@$(WITH_ENV) python -W ignore -m tests.init.add_oauth
	@$(WITH_ENV) python -W ignore -m tests.init.add_wallet
	@$(WITH_ENV) python -W ignore -m tests.init.add_zhiwang
	@$(WITH_ENV) python -W ignore -m tests.init.add_placebo
	@$(WITH_ENV) python -W ignore -m tests.init.add_redeemcode
	@$(WITH_ENV) python -W ignore -m tests.init.add_vendor
	@$(WITH_ENV) python -W ignore -m tests.init.add_lottery_gift


fillup-remote:
	@$(WITH_ENV) python -m jupiter.cli zhiwang init
	@$(WITH_ENV) python -m jupiter.cli xinmi init
	@$(WITH_ENV) python -m jupiter.cli sxb init

remote-zhiwang:
	@echo 'Refreshing zhiwang code'
	@$(WITH_ENV) python -W ignore -m tests.init.add_zhiwang_code --commit

remote-firewood:
	@echo 'Adding balance to firewood'
	@$(WITH_ENV) python -W ignore -m tests.init.add_firewood

docs:
	@$(WITH_ENV) $(MAKE) -C docs html

docs-force:
	@$(WITH_ENV) $(MAKE) -C docs clean
	@$(WITH_ENV) $(MAKE) -C docs html

list-tables:
	@cat database/schema.sql | grep 'CREATE' | awk '{print $$3}' | sed 's/`//g'

migrate-tables: old-schema.sql new-schema.sql
	@[ -n "`command -v sqlt-diff`" ] || (echo 'You need to install https://github.com/dbsrgits/sql-translator'; exit 1)
	sqlt-diff old-schema.sql=MySQL new-schema.sql=MySQL | tee database/migrations/`date +%Y%m%d-%H%M%S`.sql
	rm old-schema.sql new-schema.sql

old-schema.sql:
	git show HEAD:database/schema.sql > old-schema.sql

new-schema.sql:
	git show :database/schema.sql > new-schema.sql
