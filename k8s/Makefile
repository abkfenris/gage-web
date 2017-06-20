#etcd:
	# create etcd cluster that patroni will talk to
#	kubectl apply -f etcd-cluster.yaml

config:
	# kubectl create -f sec-patroni.yaml
	kubectl create configmap patroni-template --from-file=configs/patroni.template.yml
	kubectl create secret generic patroni-wale --from-file=configs/google-wale.json
	kubectl create -f wale-config.yaml
	kubectl create -f riverflows-config.yaml
	kubectl create -f riverflows-secrets.yaml



patroni:
	kubectl create -f ps-patroni-ephemeral.yaml



services:
	kubectl create -f svc-patroni-master.yaml
	kubectl create -f svc-patroni-read.yaml

all: config services patroni


status:
	kubectl exec riverflows-patroni-0 -c patroni -- patronictl --config-file /etc/patroni/patroni.yml list riverflowsDB

load-sql:
	kubectl exec riverflows-patroni-0 -c patroni -i -- /bin/bash -c 'gosu postgres psql gage-web' < sql/gage.sql

redis:
	kubectl create -f redis.yaml

certs:
	kubectl create -f riverflo-ws.yaml

nginx:
	kubectl create configmap riverflows-nginx --from-file=configs/riverflows.conf
	kubectl create -f nginx.yaml

nginx-service:
	kubectl create -f nginx-service.yaml

web-service:
	kubectl create -f web-service.yaml

etcd-statefulset:
	helm install --name riverflows-etcd-set -f etcd-statefulset-values.yaml incubator/etcd