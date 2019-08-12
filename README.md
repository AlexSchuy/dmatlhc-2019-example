# dmatlhc-2019-example
Working example for DMsimp_s_spin1 model for dm@lhc 2019. Shows how to generate events with madgraph + pythia, run event selection with rivet, and calculate CLs with pyhf.

## Workflow
There are two steps to running the workflow. First, run `docker run -it --rm -v $PWD:/contur/volume smeehan12/dmatlhc2019-tutorial:v0 bash` within the `runarea` directory. Next, from within the contur directory in the docker image, run `python volume/run.py` with appropriate inputs. Plots and such will be output to the appropriate runarea/{shower}_{model} directory, e.g., runarea/pythia_axial if you use pythia for generation and the DMsimp_s_spin1 model.
