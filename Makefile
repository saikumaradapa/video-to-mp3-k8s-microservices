SERVICES = rabbitmq mysql mongodb mailhog auth converter gateway notification
MANIFEST_BASE = ./src
CLUSTER_MANIFESTS = ./cluster/manifests

.PHONY: apply delete apply-% delete-% ns-up ns-delete

# Apply all service manifests (CMD/PowerShell compatible)
apply:
	$(foreach svc,$(SERVICES),kubectl apply -f $(MANIFEST_BASE)/$(svc)/manifests &&) echo Done.

# Delete all service manifests
delete:
	$(foreach svc,$(SERVICES),kubectl delete -f $(MANIFEST_BASE)/$(svc)/manifests &&) echo Done.

# Apply specific service
apply-%:
	kubectl apply -f $(MANIFEST_BASE)/$*/manifests

# Delete specific service
delete-%:
	kubectl delete -f $(MANIFEST_BASE)/$*/manifests

# Setup namespace and associated policies
ns-up:
	kubectl apply -f $(CLUSTER_MANIFESTS)/namespace.yaml
	kubectl apply -f $(CLUSTER_MANIFESTS)/limit-range.yaml
	kubectl apply -f $(CLUSTER_MANIFESTS)/resource-quota.yaml

# Delete namespace and associated policies
ns-delete:
	kubectl delete -f $(CLUSTER_MANIFESTS)/resource-quota.yaml
	kubectl delete -f $(CLUSTER_MANIFESTS)/limit-range.yaml
	kubectl delete -f $(CLUSTER_MANIFESTS)/namespace.yaml
