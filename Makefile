

build:
	docker build . -t codeshield-app:v1 --no-cache

tag:
	docker tag codeshield-app:v1 env-rbnfrhnrtest-registry.jcloud.ik-server.com/codeshield-app:v1


push:
	docker push env-rbnfrhnrtest-registry.jcloud.ik-server.com/codeshield-app:v1

build-push: build tag push