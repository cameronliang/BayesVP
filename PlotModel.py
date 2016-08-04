import numpy as np
import pylab as pl
import sys

from Model import generic_prediction
from Utilities import write_mcmc_stats

def plot_spec(obs_spec):
    c = 299792.485 # [km/s]
    burnin = 0.5 * obs_spec.nsteps #  Hardwired burnin fraction = 0.5

    mcmc_chain_fname = obs_spec.chain_fname + '.npy'
    mcmc_chain = np.load(mcmc_chain_fname)

    temp_flags = obs_spec.vp_params_flags[~np.isnan(obs_spec.vp_params_flags)]
    n_params = len(list(set(temp_flags)))
    samples = mcmc_chain[burnin:, :, :].reshape((-1, n_params))
    alpha = np.median(samples,axis=0)

    model_flux = generic_prediction(alpha,obs_spec)    

    # Write best fit parameters summary file
    summary = raw_input('Write best fit summary? (y/n): ')
    if summary == 'y':
        output_summary_fname = obs_spec.spec_path + '/vpfit_mcmc/bestfits_summary.dat' 
        write_mcmc_stats(mcmc_chain_fname,output_summary_fname)

    # Plot the best fit for visual comparison
    plotting = raw_input('Plot model comparison? (y/n): ')
    if plotting == 'y':
        rest_wave = raw_input('Enter a central wavelength or hit enter to use default wavelength: ')
        if rest_wave == "":
            # Use the first transition as the central wavelength
            rest_wave = obs_spec.transitions_params_array[0][0][0][1]
        else:
             rest_wave = float(rest_wave)
        redshift = float(raw_input('System redshift = '))
        dv = float(raw_input('Enter velocity range: '))

        obs_spec_wave = obs_spec.wave / (1+redshift) 
        obs_spec_dv = c*(obs_spec_wave - rest_wave) / rest_wave
        pl.rc('text', usetex=True)
        pl.step(obs_spec_dv,obs_spec.flux,'k',label=r'$\rm Data$')
        pl.step(obs_spec_dv,model_flux,'b',lw=2,label=r'$\rm Best\,Fit$')
        pl.step(obs_spec_dv,obs_spec.dflux,'r')
        pl.axhline(1,ls='--',c='g',lw=1.2)
        pl.axhline(0,ls='--',c='g',lw=1.2)
        pl.ylim([-0.1,1.4])
        pl.xlim([-dv,dv])
        pl.xlabel(r'$dv\,[\rm km/s]$')
        pl.ylabel(r'$\rm Normalized\,Flux$')
        pl.legend(loc=3)
        pl.savefig(obs_spec.spec_path + '/vpfit_mcmc/bestfit_spec.pdf',bbox_inches='tight',dpi=100)
        print('Written %svpfit_mcmc/bestfit_spec.pdf\n' % obs_spec.spec_path)

    # Write to file for original fitted data and best-fit model flux    
    output_model = raw_input('Write best fit model spectrum? (y/n): ')
    if output_model == 'y':
        np.savetxt(obs_spec.spec_path + '/vpfit_mcmc/bestfit_model.dat',
                np.c_[obs_spec.wave,obs_spec_dv,
                     obs_spec.flux, obs_spec.dflux,model_flux],
                header='wave\tdv\tflux\terror\tmodel')
        print('Written %svpfit_mcmc/bestfit_model.dat\n' % obs_spec.spec_path)

def main(config_fname):
    from Config import DefineParams
    obs_spec = DefineParams(config_fname)
    obs_spec.fileio_mcmc_params()
    obs_spec.fitting_data()
    obs_spec.fitting_params()
    obs_spec.spec_lsf()

    plot_spec(obs_spec)

if __name__ == '__main__':
    config_fname = sys.argv[1]
    sys.exit(int(main(config_fname) or 0))