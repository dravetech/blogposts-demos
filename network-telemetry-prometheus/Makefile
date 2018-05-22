SPINE00=prometheus_demo_spine00
LEAF00=prometheus_demo_leaf00
LEAF01=prometheus_demo_leaf01


.PHONY: start
start: stop build
	docker-compose up -d
	docker network create -d bridge --subnet 10.200.201.0/24 prometheus-nornir-snmp-replacement_link0
	docker network create -d bridge --subnet 10.200.202.0/24 prometheus-nornir-snmp-replacement_link1
	make start_ceos DEVICE=$(SPINE00) PORT=12443 IP=200
	make start_ceos DEVICE=$(LEAF00) PORT=12444 IP=201
	make start_ceos DEVICE=$(LEAF01) PORT=12445 IP=202


.PHONY: build
build:
	docker-compose build


.PHONY: stop
stop:
	docker rm -f $(SPINE00) || exit 0
	docker rm -f $(LEAF00) || exit 0
	docker rm -f $(LEAF01) || exit 0
	docker-compose down
	docker network rm prometheus-nornir-snmp-replacement_link0 || exit 0
	docker network rm prometheus-nornir-snmp-replacement_link1 || exit 0


.PHONY: start_ceos
start_ceos:
	docker create \
		--name=$(DEVICE) \
		--privileged \
		-v $(PWD)/network/$(DEVICE).cfg:/mnt/flash/startup-config \
		-p $(PORT):443 \
		-e CEOS=1 \
		-e container=docker \
		-e EOS_PLATFORM=ceossim \
		-e SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 \
		-e ETBA=1 \
		-e INTFTYPE=eth \
		ceosimage:4.20.5F /sbin/init
	docker network connect prometheus-nornir-snmp-replacement_management --ip 10.200.200.$(IP) $(DEVICE)
ifeq ($(DEVICE), $(SPINE00))
	docker network connect prometheus-nornir-snmp-replacement_link0 --ip 10.200.201.$(IP) $(DEVICE)
	docker network connect prometheus-nornir-snmp-replacement_link1 --ip 10.200.202.$(IP) $(DEVICE)
else ifeq ($(DEVICE), $(LEAF00))
	docker network connect prometheus-nornir-snmp-replacement_link0 --ip 10.200.201.$(IP) $(DEVICE)
else ifeq ($(DEVICE), $(LEAF01))
	docker network connect prometheus-nornir-snmp-replacement_link1 --ip 10.200.202.$(IP) $(DEVICE)
endif
	docker start $(DEVICE)


.PHONY: stop_ceos
stop_ceos:
	docker rm -f $(SPINE00)

.PHONY: spine00
spine00:
	docker exec -it prometheus_demo_spine00 Cli

.PHONY: leaf00
leaf00:
	docker exec -it prometheus_demo_leaf00 Cli

.PHONY: leaf01
leaf01:
	docker exec -it prometheus_demo_leaf01 Cli
