# Pull latest CentOS image
FROM continuumio/miniconda3

# Creator
MAINTAINER Sam Potter <spotter1642@gmail.com>

# Define the shell
SHELL ["/bin/bash", "-c"]

# Install conda
RUN conda update -q conda
RUN conda create -q -n test-env python=3.6 pytest pytest-cov
RUN conda activate test-env
RUN conda install numpy