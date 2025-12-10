# Kubernetes Deployment for Lab2 Application

This directory contains Kubernetes manifests to deploy the Flask application with PostgreSQL database, converted from the docker-compose.yml configuration.

## Components

- **PostgreSQL Database**: Deployment with persistent storage
- **Database Initialization**: Init container in web deployment that creates tables and inserts initial data
- **Flask Web Application**: Deployment with health checks

## Manifests

1. `pg_secret.yml` - Kubernetes Secret containing database credentials
2. `pg_pvc.yml` - PersistentVolumeClaim for database storage
3. `pg_deployment.yml` - PostgreSQL Deployment
4. `pg_service.yml` - PostgreSQL Service (ClusterIP)
5. `web_deployment.yml` - Flask application Deployment with init container for DB initialization
6. `web_service.yml` - Flask application Service (ClusterIP)

## Prerequisites

1. Kubernetes cluster (kind cluster is already created)
2. Docker image `lab2_flask_app:latest` built and available

### Building the Docker Image

If you need to build the Docker image:

```bash
cd /Users/germankochnev/Desktop/projects/itmo/containers/lab4-kubernetes-2
docker build -f Dockerfile.good -t lab2_flask_app:latest .
```

For kind cluster, you need to load the image:

```bash
kind load docker-image lab2_flask_app:latest
```

## Deployment Order

Deploy the manifests in the following order:

```bash
# 1. Create secret
kubectl apply -f pg_secret.yml

# 2. Create persistent volume claim
kubectl apply -f pg_pvc.yml

# 3. Deploy PostgreSQL database
kubectl apply -f pg_deployment.yml
kubectl apply -f pg_service.yml

# 4. Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=lab2,component=db --timeout=120s

# 5. Deploy web application (init container will handle DB initialization)
kubectl apply -f web_deployment.yml
kubectl apply -f web_service.yml
```

## Database Initialization

The database initialization is handled by an **init container** in the web deployment. The init container:
1. Waits for the PostgreSQL database to be ready
2. Creates the `items` table if it doesn't exist
3. Truncates the table and inserts initial data (item1, item2, item3)

This approach is cleaner than using a separate Job because:
- The initialization runs automatically before the web container starts
- It's part of the pod lifecycle
- No need to manage a separate Job resource
- The web pod won't start until initialization is complete

## Accessing the Application

Since no Ingress is configured, use port forwarding:

```bash
# Forward local port 8080 to the web service
kubectl port-forward service/web-service 8080:5000
```

Then access the application at: http://localhost:8080

## Verification

Check the status of all components:

```bash
# Check pods
kubectl get pods -l app=lab2

# Check services
kubectl get services -l app=lab2

# View logs
kubectl logs -l app=lab2,component=web
kubectl logs -l app=lab2,component=db

# View init container logs (to see initialization)
kubectl logs -l app=lab2,component=web -c init-db
```

## Secrets

All sensitive data (database credentials) are stored in Kubernetes Secrets (`pg_secret.yml`). The secret contains:
- `POSTGRES_USER`: postgres
- `POSTGRES_PASSWORD`: postgres
- `POSTGRES_DB`: lab2db

## Cleanup

To remove all resources:

```bash
kubectl delete -f web_service.yml
kubectl delete -f web_deployment.yml
kubectl delete -f pg_service.yml
kubectl delete -f pg_deployment.yml
kubectl delete -f pg_pvc.yml
kubectl delete -f pg_secret.yml
```

Or delete by label:

```bash
kubectl delete all,pvc,secret -l app=lab2
```

