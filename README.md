# DM@LHC 2019 Tutorial Example

## Introduction
This example shows how to run a complete truth-level, particle-level analysis workflow for a simplified dark matter model. We start with a UFO description of the DM model for a signal point, and end with CLs upper limits on signal strength. 

Note: this example uses a docker image; make sure docker is installed and correctly operating (https://docs.docker.com/install/) before continuing.

The workflow consists of three broad steps: event generation, event selection and statistics. Event generation is handled by MadGraph5_aMC@NLO (https://launchpad.net/mg5amcnlo) and PYTHIA 8 (http://home.thep.lu.se/~torbjorn/Pythia.html). Event selection is handled by RIVET (https://rivet.hepforge.org/) using an ATLAS analysis (https://rivet.hepforge.org/analyses/ATLAS_2017_I1609448.html). Statistics is handled by pyhf (https://diana-hep.org/pyhf/index.html), with the addition of simulated background and collision data that is saved on HEPdata (https://www.hepdata.net/record/ins1609448).

Reference outputs for each step can be found in the reference_outputs directory.

## Generation
There are two parts to generation: first, madgraph generates unphysical, parton-level events described in the LHE format; second, pythia showers the events to create physical, particle-level events described in the HEPMC format.

### Madgraph
First, it is necessary to create a param_card for the particular point in the DMA model's parameter space that you wish to examine. To do so, please run the provided python script `make_madgraph_card.py` (try `python make_madgraph_card.py -h` to see available options). 

Next, run `. start_docker.sh` to run the docker image for this tutorial. Within the docker image, run `mg5_aMC` to start madgraph. Within madgraph, enter the following commands:
1. `import model DMsimp_s_spin1 --modelname` (**important**: `--modelname` tells madgraph to use particle names from the UFO model; without this option, you will get confusing errors). 
2. `generate p p > xd xd~ j`
3. `output {my_output_dir}` with `{my_output_dir}` replaced with your choice.
4. `launch`
5. `0` (PYTHIA showering should be OFF as we'll do it manually later)
6. `/inputs/cards/mMed_{mediator mass}_mDM_{dark matter mass}/param_card.dat` -- this should have been generated when you ran `make_madgraph_card.py` earlier.
7. `0`

### Pythia
You should now have a file `{my_output_dir}/Events/run_01/unweighted_events.lhe.gz`. Unzip the file with `gunzip` and run `make_pythia_card.py` with appropriate inputs to create a `pythia_card.dat`. Once that is complete, you can run `pythia_example pythia_card.dat {output hepmc}` to shower the events with pythia.

## Selection
Next, we run rivet to select events. To do so, run `rivet -a $RIVET_ANALYSIS -H {output yoda} {output hepmc}`. If you wish to see some plots of the output histograms, run `rivet-mkhtml {output yoda}`.

## Statistics
[To be continued...]
