echo "Mapping current directory to /inputs in the docker image."
docker run --rm -it -v $PWD:/inputs dmatlhc2019/empty bash