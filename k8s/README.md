# k3s deployment

This directory contains starter manifests for running the Baeksung Bus backend
and MySQL on k3s.

## Files

- `namespace.yaml`: Kubernetes namespace.
- `secret.example.yaml`: Secret template. Copy this to `secret.yaml` and fill real values.
- `configmap.yaml`: Non-secret runtime configuration.
- `mysql.yaml`: MySQL Service, init ConfigMap, StatefulSet, and PVC.
- `deploy.yaml`: Backend Deployment and Service.
- `ingress.yaml`: Traefik Ingress for `bs.baeksung.kr/api`.
  TLS certificate issuance is owned by the frontend Ingress.
- `kustomization.yaml`: Optional Kustomize entrypoint.

## Before applying

1. Build and push the backend image from this repository.
2. Replace this image name in `deploy.yaml`:
   - `ghcr.io/your-org/baeksungbus-api:latest`
3. Copy `secret.example.yaml` to `secret.yaml`, fill real values, and never commit it.
4. Review the `baeksungbus-mysql-init` ConfigMap in `mysql.yaml`.
   It currently contains this repository's `init.sql` contents.

## Apply

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/mysql.yaml
kubectl apply -f k8s/deploy.yaml
kubectl apply -f k8s/ingress.yaml
```

## GitHub Actions deployment

The workflow at `.github/workflows/deploy.yaml` builds and pushes the backend
image, copies this `k8s/` directory to the k3s server, creates/updates the
Kubernetes Secret and Docker Hub pull secret from GitHub Actions secrets,
replaces the backend image placeholder, and runs `kubectl apply`.

Required GitHub Environment or Repository secrets:

- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `SSH_HOST`
- `SSH_PORT`
- `SSH_USER`
- `SSH_PRIVATE_KEY`
- `DB_USER`
- `DB_PASSWORD`
- `MYSQL_ROOT_PASSWORD`
- `MIDDLEWARE_SECRET`
- `DOCS_ID`
- `DOCS_PASSWORD`
- `EMAIL_USERNAME`
- `EMAIL_PASSWORD`
- `EMAIL_SERVER`
- `EMAIL_PORT`

Or, after adding `secret.yaml` to `kustomization.yaml`:

```bash
kubectl apply -k k8s
```

## Notes

- k3s usually ships with Traefik as the default Ingress controller.
- The TLS annotation assumes cert-manager and a `letsencrypt-prod` ClusterIssuer.
  If you do not use cert-manager, remove the cert-manager annotation and TLS block.
- Frontend deployment should live in the `baeksungbus_web` repository.
- The backend Ingress references `baeksungbus-tls`, but the frontend Ingress
  owns cert-manager issuance for that shared host certificate.
- Keeping backend Kubernetes manifests in this repository is fine for a small deployment.
  If frontend and backend are later released as one unit, a separate `baeksungbus_ops`
  deployment repository can be cleaner.
