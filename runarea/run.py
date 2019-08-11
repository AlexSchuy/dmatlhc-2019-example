import argparse
import subprocess
import os
import numpy as np
import glob

model_name = {'axial': 'DMsimp_s_spin1', 'vector': 'DM_vector_mediator_UFO'}

contur_module_dir = os.environ['CONTURMODULEDIR']


def copy_model(model, shower):
    if shower == 'pythia':
        subprocess.call('cp -r {0}/Models/DM/{1} {0}/MG5_aMC_v2_6_6/models/'.format(
            contur_module_dir, model_name[model]), shell=True)
    elif shower == 'herwig':
        subprocess.call('cp -r {0}/AnalysisTools/GridSetup/GridPack .; cd GridPack; cp -r {0}/Models/DM/{1} .; ufo2herwig {1}; make'.format(
            contur_module_dir, model_name[model]), shell=True)


def make_param_file(volume, model, n_med, n_dm, med_lo, med_hi, dm_lo, dm_hi):
    template_path = '{0}/{1}/templates/herwig/{2}/param_file.dat'.format(
        contur_module_dir, volume, model)
    output_path = '{0}/{1}/herwig_{2}/grid/param_file.dat'.format(
        contur_module_dir, volume, model)
    with open(template_path, 'r') as template_fd:
        with open(output_path, 'w+') as output_fd:
            text = template_fd.read()
            text = text.format(n_med=n_med, med_lo=med_lo,
                               med_hi=med_hi, n_dm=n_dm, dm_lo=dm_lo, dm_hi=dm_hi)
            output_fd.write(text)
    return output_path


def make_param_card(volume, model, n_med, n_dm, med_lo, med_hi, dm_lo, dm_hi):
    def formatted_string(arr):
        formatted = ['{:.6e}'.format(a) for a in arr]
        return ', '.join(formatted)
    m_med = formatted_string(np.linspace(med_lo, med_hi, n_med))
    m_dm = formatted_string(np.linspace(dm_lo, dm_hi, n_dm))
    template_path = '{0}/{1}/templates/pythia/{2}/grid_param_card.dat'.format(
        contur_module_dir, volume, model)
    output_path = '{0}/{1}/pythia_{2}/grid/param_card.dat'.format(
        contur_module_dir, volume, model)
    with open(template_path, 'r') as template_fd:
        with open(output_path, 'w+') as output_fd:
            text = template_fd.read()
            text = text.format(m_med=m_med, m_dm=m_dm)
            output_fd.write(text)
    return output_path


def make_proc_card(volume, model, n_events, param_card):
    template_path = '{0}/{1}/templates/pythia/proc_card.dat'.format(
        contur_module_dir, volume)
    output_path = '{0}/{1}/pythia_{2}/proc_card.dat'.format(
        contur_module_dir, volume, model)
    if model == 'axial':
        process = 'p p > xd xd~ j'
    elif model == 'vector':
        process = 'p p > xm xm j'
    with open(template_path, 'r') as template_fd:
        with open(output_path, 'w+') as output_fd:
            text = template_fd.read()
            text = text.format(model=model_name[model], process=process,
                               param_card=param_card, n_events=n_events)
            output_fd.write(text)
    return output_path


def run_point(volume, model, shower, n_events):
    copy_model(model, shower)
    if shower == 'pythia':
        param_card = '{0}/{1}/pythia_{2}/point/param_card.dat'.format(
            contur_module_dir, volume, model)
        proc_card = make_proc_card(volume, model, n_events, param_card)
        subprocess.call(
            './MG5_aMC_v2_6_6/bin/mg5_aMC {0}'.format(proc_card), shell=True)
        subprocess.call(
            'mv output/Events/run_01/tag_1_pythia8_events.hepmc.gz LHC.hepmc.gz; gunzip -f LHC.hepmc.gz', shell=True)
    elif shower == 'herwig':
        input_card = '{0}/{1}/herwig_{2}/point/LHC.in'.format(
            contur_module_dir, volume, model)
        subprocess.call(
            'Herwig read {0} -I GridPack -L GridPack'.format(input_card), shell=True)
        subprocess.call(
            'Herwig run LHC.run -N {0}'.format(n_events), shell=True)
        subprocess.call('mv LHC.log {0}/{1}/{2}_{3}/point'.format(
            contur_module_dir, volume, shower, model), shell=True)
    subprocess.call(
        'rivet -a ATLAS_2017_I1609448 LHC.hepmc -o LHC.yoda', shell=True)
    subprocess.call('contur -f LHC.yoda; contur-mkhtml LHC.yoda', shell=True)
    subprocess.call('mv LHC.hepmc {0}/{1}/{2}_{3}/point'.format(
        contur_module_dir, volume, shower, model), shell=True)
    subprocess.call('mv LHC.yoda {0}/{1}/{2}_{3}/point'.format(
        contur_module_dir, volume, shower, model), shell=True)
    subprocess.call('mv -r plots {0}/{1}/{2}_{3}/point'.format(
        contur_module_dir, volume, shower, model), shell=True)
    subprocess.call('mv -r ANALYSIS {0}/{1}/{2}_{3}/point'.format(
        contur_module_dir, volume, shower, model), shell=True)
    subprocess.call('mv -r contur-plots {0}/{1}/{2}_{3}/point'.format(
        contur_module_dir, volume, shower, model), shell=True)
    subprocess.call('mv contur.log {0}/{1}/{2}_{3}/point'.format(
        contur_module_dir, volume, shower, model), shell=True)


def run_grid(volume, model, shower, n_events, n_med, n_dm, med_lo, med_hi, dm_lo, dm_hi):
    copy_model(model, shower)
    if shower == 'pythia':
        param_card = make_param_card(
            volume, model, n_med, n_dm, med_lo, med_hi, dm_lo, dm_hi)
        proc_card = make_proc_card(volume, model, n_events, param_card)
        subprocess.call(
            './MG5_aMC_v2_6_6/bin/mg5_aMC {0}'.format(proc_card), shell=True)
    elif shower == 'herwig':
        param_file = make_param_file(
            volume, model, n_med, n_dm, med_lo, med_hi, dm_lo, dm_hi)
        input_card = '{0}/{1}/herwig_{2}/grid'.format(
            contur_module_dir, volume, shower)
        subprocess.call('rm -rf myscan00', shell=True)
        subprocess.call('cp {0} .; cp {1} .; batch-submit -n {2} --seed 101 -s -P'.format(
            param_file, input_card, n_events), shell=True)
        for run_script in glob.glob('myscan00/13TeV/*/*.sh'):
            subprocess.call('./{0}'.format(run_script), shell=True)
        subprocess.call('contur -g myscan00/', shell=True)
        subprocess.call('contur-plot myscan00/13TeV/ANALYSIS/contur.map mXd mY1')
            

def main():
    parser = argparse.ArgumentParser(description="Run workflow for DM@LHC 2019 tutorial.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--model', '-m', required=True, choices=[
                        'vector', 'axial'], help='The type of model to use. vector = DM_vector_mediator_UFO, axial = DMsimp_s_spin1.')
    parser.add_argument('--shower', '-s', required=True,
                        choices=['pythia', 'herwig'], help='The program to use for showering.')
    parser.add_argument('--n_events', '-n', default=200,
                        help='The number of events to use for each point.')
    parser.add_argument('--volume', '-v', default='volume',
                        help='The path of the mounted volume in the docker image.')
    subparsers = parser.add_subparsers(dest='type')
    point_parser = subparsers.add_parser(
        'point', help='Run the workflow for a single point.')
    grid_parser = subparsers.add_parser(
        'grid', help='Run the workflow for a grid of points.')

    grid_parser.add_argument(
        '-n_med', default=3, help='Number of mediator masses to use.')
    grid_parser.add_argument(
        '-n_dm', default=3, help='Number of DM masses to use.')
    grid_parser.add_argument('-med_lo', default=10,
                             help='Minimum mediator mass (GeV).')
    grid_parser.add_argument('-med_hi', default=3600,
                             help='Maximum mediator mass (GeV).')
    grid_parser.add_argument('-dm_lo', default=10,
                             help='Minimum DM mass (GeV).')
    grid_parser.add_argument('-dm_hi', default=3610,
                             help='Maximum DM mass (GeV).')

    args = parser.parse_args()
    if args.type == 'point':
        run_point(args.volume, args.model, args.shower, args.n_events)
    elif args.type == 'grid':
        run_grid(args.volume, args.model, args.shower, args.n_events, args.n_med, args.n_dm,
                 args.med_lo, args.med_hi, args.dm_lo, args.dm_hi)


if __name__ == '__main__':
    main()
