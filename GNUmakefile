### https://tech.davis-hansson.com/p/make/
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -o errexit -o nounset -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
.RECIPEPREFIX = >
###

# venv_dir := .venv
# venv_bin := ${venv_dir}/bin
# venv_python := ${venv_bin}/python3
tool_piptools_container := piptools

tool_run := docker run \
  --rm \
  --volume $(shell pwd):/work \
  --workdir /work \
  --user $(shell id -u):$(shell id -g)
tool_piptools_run := ${tool_run} ${tool_piptools_container}
tool_pipcompile_run := ${tool_piptools_run} --cache-dir=/tmp/piptoolscache --quiet --generate-hashes
tool_builder_run := ${tool_run} ${tool_builder_container}

alpine_deps := alpine/files alpine/tools alpine/.dockerignore
debian_deps := debian/files debian/tools debian/.dockerignore
global_template_deps := tools/Dockerimage.builder update.py vars.toml

image_tag := red


.PHONY: build
build: $(all_image_targets)

.PHONY: clean
clean:
> rm -rf tools/Dockerimage.*
> docker rmi --force ${tool_piptools_container}

tools/Dockerimage.piptools: tools/Dockerfile.piptools
> docker build \
  --file $< \
  --tag ${tool_piptools_container} \
  --iidfile $@ \
  .

requirements.txt: requirements.in tools/Dockerimage.piptools
> ${tool_pipcompile_run} --output-file=$@ $<

tools/Dockerimage.builder: tools/Dockerfile.builder requirements.txt
> docker build \
  --file $< \
  --tag ${tool_builder_container} \
  --iidfile $@ \
  .
