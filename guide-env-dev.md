# Guia para configurar el entorno de desarrollo

## Actualizar ubuntu
```bash
sudo apt-get update
sudo apt-get upgrade
```

# Frontend
## Instalar node 20+
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm list-remote
nvm install v22.18.0
node -v
```

## Actualizar npm
```bash
npm install -g npm@11.5.2
npm -v
```

# Backend
## Verificar la versión de python
```bash
python3 --version
```

## Instalar poetry
```bash
sudo apt install pipx -y
pipx ensurepath
pipx install poetry
pipx ensurepath
poetry --version
```

## Instalar dependencias
```bash
poetry install
```

## Activar entorno virtual
```bash
poetry env activate
source /home/osboxes/.cache/pypoetry/virtualenvs/backend-LjU6nvWn-py3.12/bin/activate
```

## Agregar nuevas dependencias a poetry
