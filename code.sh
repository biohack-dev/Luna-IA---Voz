# Atualize os pacotes
sudo apt update

# Instale dependências necessárias
sudo apt install software-properties-common apt-transport-https wget

# Adicione a chave GPG do repositório do VS Code
wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | sudo apt-key add -

# Adicione o repositório do VS Code
sudo add-apt-repository "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main"

# Atualize os pacotes novamente e instale o VS Code
sudo apt update
sudo apt install code
