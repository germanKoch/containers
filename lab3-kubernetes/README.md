# Лабораторная работа №3: Kubernetes

## 1. Перенос POSTGRES_USER и POSTGRES_PASSWORD в Secret

### Создан новый манифест: `pg_secrets.yml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  labels:
    app: nextcloud
type: Opaque
stringData:
  POSTGRES_USER: "postgres"
  POSTGRES_PASSWORD: "postgres"

### Изменения в `pg_configmap.yml`

**Удалено:**
```yaml
POSTGRES_USER: "postgres"
POSTGRES_PASSWORD: "postgres"
```

**Осталось только:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-configmap
  labels:
    app: postgres
data:
  POSTGRES_DB: "postgres"
```

### Изменения в `pg_deployment.yml`

Переменные `POSTGRES_USER` и `POSTGRES_PASSWORD` теперь берутся из Secret вместо ConfigMap:

**Было (configMapKeyRef):**
```yaml
env:
  - name: POSTGRES_USER
    valueFrom:
      configMapKeyRef:
        name: postgres-configmap
        key: POSTGRES_USER
  - name: POSTGRES_PASSWORD
    valueFrom:
      configMapKeyRef:
        name: postgres-configmap
        key: POSTGRES_PASSWORD
```

**Стало (secretKeyRef):**
```yaml
env:
  - name: POSTGRES_USER
    valueFrom:
      secretKeyRef:
        name: postgres-secret
        key: POSTGRES_USER
  - name: POSTGRES_PASSWORD
    valueFrom:
      secretKeyRef:
        name: postgres-secret
        key: POSTGRES_PASSWORD
```

---

## 2. Перенос переменных Nextcloud в ConfigMap

### Создан новый манифест: `nextcloud_configmap.yml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nextcloud-configmap
  labels:
    app: nextcloud
data:
  NEXTCLOUD_UPDATE: "1"
  ALLOW_EMPTY_PASSWORD: "yes"
```

### Изменения в `nextcloud.yml`

Переменные `NEXTCLOUD_UPDATE` и `ALLOW_EMPTY_PASSWORD` вынесены из захардкоженных значений в ConfigMap:

**Было (hardcoded):**
```yaml
env:
  - name: NEXTCLOUD_UPDATE
    value: "1"
  - name: ALLOW_EMPTY_PASSWORD
    value: "yes"
```

**Стало (configMapKeyRef):**
```yaml
env:
  - name: NEXTCLOUD_UPDATE
    valueFrom:
      configMapKeyRef:
        name: nextcloud-configmap
        key: NEXTCLOUD_UPDATE
  - name: ALLOW_EMPTY_PASSWORD
    valueFrom:
      configMapKeyRef:
        name: nextcloud-configmap
        key: ALLOW_EMPTY_PASSWORD
```

---

## 3. Создание Service для Nextcloud

### Создан новый манифест: `nextcloud_service.yml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nextcloud-service
  labels:
    app: nextcloud
spec:
  type: NodePort
  ports:
   - port: 80
     targetPort: 80
     protocol: TCP
     name: http
  selector:
   app: nextcloud
```

Service типа NodePort позволяет получить доступ к Nextcloud UI с вашего ноутбука без использования Ingress.

### Изменения в `nextcloud.yml`

Обновлена переменная `NEXTCLOUD_TRUSTED_DOMAINS` для поддержки внешнего доступа:

**Было:**
```yaml
- name: NEXTCLOUD_TRUSTED_DOMAINS
  value: "127.0.0.1"
```

**Стало:**
```yaml
- name: NEXTCLOUD_TRUSTED_DOMAINS
  value: "127.0.0.1 localhost"
```

---

## 4. Добавление Liveness и Readiness проб для Nextcloud

### Изменения в `nextcloud.yml`

Добавлены пробы для проверки состояния контейнера:

```yaml
livenessProbe:
  httpGet:
    path: /status.php
    port: 80
    httpHeaders:
    - name: Host
      value: localhost
  initialDelaySeconds: 60
  periodSeconds: 30
  timeoutSeconds: 5
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /status.php
    port: 80
    httpHeaders:
    - name: Host
      value: localhost
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

**Параметры проб:**
- `livenessProbe` — проверяет, жив ли контейнер. При неудаче контейнер перезапускается.
- `readinessProbe` — проверяет, готов ли контейнер принимать трафик.
- `initialDelaySeconds` — задержка перед первой проверкой (60 сек для liveness, 30 сек для readiness)
- `periodSeconds` — интервал между проверками
- `failureThreshold` — количество неудачных проверок до срабатывания

## Порядок применения манифестов

### 1. Применяем ConfigMaps и Secrets
```bash
kubectl apply -f pg_configmap.yml
kubectl apply -f pg_secrets.yml
kubectl apply -f nextcloud_configmap.yml
```
![1](./screenshots/1.png)

### 2. Применяем PostgreSQL
```bash
kubectl apply -f pg_deployment.yml
kubectl apply -f pg_service.yml
```
![2](./screenshots/2.png)

### 3. Применяем Nextcloud
```bash
kubectl apply -f nextcloud.yml
kubectl apply -f nextcloud_service.yml
```
![3](./screenshots/3.png)

### 4. Проверяем статус подов
```bash
kubectl get pods
```
![4](./screenshots/4.png)

---

## Доступ к Nextcloud UI

### Выполненные действия

#### 1. Создание Service для Nextcloud

**Действия:**
- Создан новый манифест `nextcloud_service.yml` с определением Service типа `NodePort`
- Service настроен на проброс порта 80 контейнера Nextcloud на внешний порт кластера
- Service использует селектор `app: nextcloud` для маршрутизации трафика к подам

**Содержимое `nextcloud_service.yml`:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nextcloud-service
  labels:
    app: nextcloud
spec:
  type: NodePort
  ports:
   - port: 80
     targetPort: 80
     protocol: TCP
     name: http
  selector:
   app: nextcloud
```

**Применение:**
```bash
kubectl apply -f nextcloud_service.yml
```

#### 2. Обновление конфигурации Nextcloud для внешнего доступа

**Действия:**
- Обновлена переменная окружения `NEXTCLOUD_TRUSTED_DOMAINS` в манифесте `nextcloud.yml`
- Добавлен `localhost` в список доверенных доменов (ранее был только `127.0.0.1`)

**Изменения в `nextcloud.yml`:**
```yaml
# Было:
- name: NEXTCLOUD_TRUSTED_DOMAINS
  value: "127.0.0.1"

# Стало:
- name: NEXTCLOUD_TRUSTED_DOMAINS
  value: "127.0.0.1 localhost"
```

**Применение:**
```bash
kubectl apply -f nextcloud.yml
```

#### 3. Проброс порта Service на локальный хост
Использование `kubectl port-forward` для проброса порта Service на локальный хост:

```bash
kubectl port-forward svc/nextcloud-service 8080:80
```

#### 4. Доступ к Nextcloud UI
![5](./screenshots/5.png)
