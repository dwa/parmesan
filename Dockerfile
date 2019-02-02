FROM fedora:29

RUN dnf -y -q update
RUN dnf -y -q groupinstall "Development Tools"
RUN dnf -y -q groupinstall "C Development Tools and Libraries"
RUN dnf -y -q install libxml2-devel redhat-rpm-config python3-devel wget bzip2

WORKDIR /

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda3

ENV PATH="/miniconda3/bin:${PATH}"

#RUN export PATH="miniconda3/bin:$PATH"
RUN . /miniconda3/etc/profile.d/conda.sh
RUN echo ". /miniconda3/etc/profile.d/conda.sh" >> /root/.bashrc
RUN conda update --all --yes
RUN conda install --yes pkgconfig pkg-config pkgconfig libxml2
RUN pip install cppyy
RUN conda install --yes ipython numpy pandas pyarrow click
# only for py3.6 available for now:
#RUN conda install --yes -c bioconda snakemake
RUN conda install --yes datrie wrapt pyyaml appdirs docutils configargparse jsonschema gitdb2 smmap2 gitpython
RUN conda install --yes -c conda-forge ratelimiter
RUN pip install snakemake
