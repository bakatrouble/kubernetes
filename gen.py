#!/usr/bin/env python3

from mako.template import Template
from pathlib import Path
import sys


NS_TEMPLATE = Template('''\
apiVersion: v1
kind: Namespace
metadata:
  name: ${name}
''')


DEPLOYMENT_TEMPLATE = Template('''\
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: ${name}
  name: ${name}
  namespace: ${name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ${name}
  template:
    metadata:
      labels:
        app: ${name}
    spec:
      containers:
      - nodeName: htpc.local
        env:
        - name: ENV
          value: value
        image: image:latest
        name: ${name}
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "4"
            memory: 3096Mi
          requests:
            cpu: "1"
            memory: 1Gi
        volumeMounts:
        - mountPath: /path/inside/container
          name: ${name}-storage
      volumes:
      - hostPath:
          path: /external/path
          name: ${name}-storage
''')


SERVICE_TEMPLATE = Template('''\
apiVersion: v1
kind: Service
metadata:
  labels:
    app: ${name}
  name: ${name}
  namespace: ${name}
spec:
  ports:
  - port: 8000
  selector:
    app: ${name}
''')


INGRESS_TEMPLATE = Template('''\
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: ${name}-ingress
  namespace: ${name}
spec:
  entryPoints:
  - websecure
  routes:
  - kind: Rule
    match: Host(`${name}.home.bakatrouble.me`)
    services:
    - kind: Service
      name: ${name}
      namespace: ${name}
      port: 8000
  tls:
    certResolver: default
''')


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else input('Project name: ')
    print(f'Project: {name}')
    deployment_num = int(input('Deployment manifest number [1]: ') or '1')
    dir = Path(name)
    dir.mkdir(exist_ok=True)

    with open(dir / f'00-{name}-ns.yaml', 'w') as f:
        f.write(NS_TEMPLATE.render(name=name))

    with open(dir / f'{deployment_num:02d}-{name}-deployment.yaml', 'w') as f:
        f.write(DEPLOYMENT_TEMPLATE.render(name=name))
        deployment_num += 1

    with open(dir / f'{deployment_num:02d}-{name}-service.yaml', 'w') as f:
        f.write(SERVICE_TEMPLATE.render(name=name))
        deployment_num += 1

    with open(dir / f'{deployment_num:02d}-{name}-ingress.yaml', 'w') as f:
        f.write(INGRESS_TEMPLATE.render(name=name))

    print('Done')


if __name__ == '__main__':
    main()
