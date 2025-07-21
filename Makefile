SERVICES = mysql mongodb auth rabbitmq
MANIFEST_BASE = ./src

.PHONY: apply delete apply-% delete-%

# Apply all manifests (CMD/PowerShell compatible)
apply:
	$(foreach svc,$(SERVICES),kubectl apply -f $(MANIFEST_BASE)/$(svc)/manifests &&) echo Done.

# Delete all manifests
delete:
	$(foreach svc,$(SERVICES),kubectl delete -f $(MANIFEST_BASE)/$(svc)/manifests &&) echo Done.

# Apply specific service
apply-%:
	kubectl apply -f $(MANIFEST_BASE)/$*/manifests

# Delete specific service
delete-%:
	kubectl delete -f $(MANIFEST_BASE)/$*/manifests
