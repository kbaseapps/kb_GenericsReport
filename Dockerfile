FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

RUN echo "start building docker image"
RUN apt-get update --fix-missing
RUN apt-get install -y gcc wget

RUN pip install --upgrade pip \
    && python --version

RUN pip install coverage==5.5

RUN pip install numpy==1.19.1 \
    && pip install pandas==1.1.1 --ignore-installed certifi \
    && pip install matplotlib==3.3.1 \
    && pip install scipy==1.5.2 \
    && pip install plotly==4.9.0 \
    && pip install psutil==5.7.2 \
    && pip install requests==2.24.0 \
    && pip install datashader==0.11.1 \
    &&  pip install xlrd==1.2.0

# RUN conda install -y -c plotly plotly-orca \
#     && python --version
# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
