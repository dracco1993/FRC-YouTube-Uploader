FROM linuxserver/ffmpeg:latest

# Get base system dependencies
RUN apt-get update && apt-get install -y \
  wget \
  curl \
  unzip \
  sudo \
  jq \
  tmux \
  vim \
  openssh-server \
  python3-pip

# Start splitting server
# CMD ["/some/commanad", "-param1", "-param2]
