# https://esgf-data.dkrz.de/esg-search/wget/?distrib=false&dataset_id=cordex.output.EUR-11.CLMcom-ETH.MPI-M-MPI-ESM-LR.historical.r1i1p1.COSMO-crCLIM-v1-1.v1.6hr.hus200.v20191219|esgf1.dkrz.de
# https://esgf-data.dkrz.de/esg-search/wget/?distrib=false&dataset_id=cordex.output.EUR-11.CLMcom-ETH.MOHC-HadGEM2-ES.rcp85.r1i1p1.COSMO-crCLIM-v1-1.v1.6hr.hus200.v20200924|esgf1.dkrz.de
import urllib
import os, stat, subprocess, math
import urllib.request

# https://esgf-node.ipsl.upmc.fr/esg-search/wget?latest=true&realm=atmos&project=CMIP6&experiment_id=historical&frequency=6hrPt&member_id=r1i1p1f1&variable=ta&variable=ua&source_id=NESM3&limit=1000

# bash name, model und experiment

# https://esgf-node.ipsl.upmc.fr/esg-search/wget?latest=true&realm=atmos&project=CMIP6&experiment_id=historical&frequency=6hrPt&table_id=6hrPlevPt&member_id=r1i1p1f1&variable=ta&source_id=EC-Earth3&limit=1000


# url_struc = "https://esgf-node.ipsl.upmc.fr/esg-search/wget?latest=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=1000"

# url_struc = "https://esgf-data.dkrz.de/esg-search/wget?latest=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=1000"
# url_struc = "https://esgf-data.dkrz.de/esg-search/wget/?distrib=false&dataset_id=CMIP6.CMIP.{gcm}.{exp}.{run}.{table_id}.{var}.gn.v20190710|esgf3.dkrz.de"

# url_struc = "https://esgf.ceda.ac.uk/esg-search/wget?distrib=true&latest=true&replica=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000"
# url_struc = "https://esgf-data.dkrz.de/esg-search/wget?distrib=true&latest=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000"
url_struc = "https://esgf-node.ipsl.upmc.fr/esg-search/wget?distrib=true&latest=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000"
# url_struc = "https://esgf-node.ornl.gov/esg-search/wget?distrib=true&latest=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000"

# outdir = '/data/reloclim/normal/CMIP6_ars/wget_scripts'  # data
outdir = '/reloclim/ars/INTERACT/CMIP6/wget_scripts'  # big data

wget_name_struc = "wget_{gcm}_{exp}_{var}_{table_id}.sh"

freqs = ['6hrPt', '6hrPt', '6hr', '3hr']
table_ids = ['6hrPlevPt', '6hrLev', '6hrPlev', '3hr']
varss = [['hus', 'va', 'ta', 'ua', 'zg'],
        ['hus', 'va', 'ta', 'ua', 'zg'],
        ['pr'],
        ['pr']]

exps = ['ssp585']
# exps = ['historical']
run = 'r1i1p1f1'

# gcms = [
#  'ACCESS-CM2',
#  'ACCESS-ESM1-5',
#  'AWI-ESM-1-1-LR',
#  'BCC-CSM2-MR',
#  'BCC-ESM1',
#  'CAS-ESM2-0',
#  'CESM2',
#  'CESM2-FV2',
#  'CESM2-WACCM',
#  'CESM2-WACCM-FV2',
#  'CIESM',
#  'CMCC-CM2-HR4',
#  'CMCC-CM2-SR5',
#  'CMCC-ESM2',
#  'CanESM5',
#  'CanESM5-1',
#  'E3SM-1-0',
#  'E3SM-1-1',
#  'E3SM-1-1-ECA',
#  'E3SM-2-0',
#  'E3SM-2-0-NARRM',
#  'EC-Earth3',
#  'EC-Earth3-AerChem',
#  'EC-Earth3-CC',
#  'EC-Earth3-Veg',
#  'EC-Earth3-Veg-LR',
#  'FGOALS-f3-L',
#  'FGOALS-g3',
#  'GFDL-CM4',
#  'GFDL-ESM',
#  'GFDL-ESM4',
#  'GISS-E2-1-G',
#  'GISS-E2-1-H',
#  'GISS-E2-2-G',
#  'GISS-E2-2-H',
#  'IPSL-CM5A2-INCA',
#  'IPSL-CM6A-LR',
#  'IPSL-CM6A-LR-INCA',
#  'KACE-1-0-G',
#  'KIOST-ESM',
#  'MCM-UA-1-0',
#  'MIROC6',
#  'MPI-ESM-1-2-HAM',
#  'MPI-ESM1-2-HR',
#  'MPI-ESM1-2-LR',
#  'MRI-ESM2-0',
#  'NESM3',
#  'NorCPM1',
#  'NorESM2-LM',
#  'NorESM2-MM',
#  'SAM0-UNICON',
#  'SAM0-UNICONACCESS-CM2',
#  'TaiESM1'
#  ]

gcms = [
#  'MPI-ESM1-2-HR',
#  'MPI-ESM1-2-LR',
#  'MRI-ESM2-0',
#  'NorESM2-LM',
 'NorESM2-MM',
#  'TaiESM1'
 ]

for gcm in gcms:
    for exp in exps:
        pr_downloaded = False
        for freq, table_id, vars in zip(freqs, table_ids, varss):
            for var in vars:

                search_url = url_struc.format(**{'gcm': gcm,
                                                'exp': exp,
                                                'run': run,
                                                'table_id': table_id,
                                                'freq': freq,
                                                'var': var})

                if not pr_downloaded:
                    response = urllib.request.urlopen(search_url)
                    data = response.read()      # a `bytes` object
                    if data == b'No files were found that matched the query':
                        print(f"query not successfull {search_url}")
                    else:
                        text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
                        wget_name = wget_name_struc.format(**{'gcm': gcm, 'exp': exp, 'freq': freq, 'table_id': table_id, 'var': var})
                        outpath = os.path.join(outdir, wget_name)
                        with open(outpath, "w") as file:
                            file.write(text)
                        if var == 'pr':
                            pr_downloaded = True


# table_id
# 6hrPlevPt

# frequency
# 6hrPt



# pr

# table_id
# 3hr
# 6hrPlev

# frequency
# 3hr
# 6hr


# '4AOP-v1-5',
# 'ACCESS1-3-rcp85-1-0',
# 'BCC-CSM2-HR',
# 'BCC-CSM2-MR',
# 'BCC-ESM1',
# 'CAS-ESM2-0',
# 'CCMI-hist-nat-1-1',
# 'CCMI-hist-sol-1-1',
# 'CCMI-hist-stratO3-1-0',
# 'CCMI-hist-volc-1-1',
# 'CCMI-ssp245-nat-1-0',
# 'CCMI-ssp245-sol-1-0',
# 'CCMI-ssp245-stratO3-1-0',
# 'CCMI-ssp245-volc-1-0',
# 'CCSM4-rcp26-1-0',
# 'CCSM4-rcp85-1-0',
# 'CEDS-2017-05-18',
# 'CEDS-2017-05-18-supplemental-data',
# 'CEDS-2017-08-30',
# 'CEDS-2017-08-30-supplemental-data',
# 'CEDS-2017-10-05',
# 'CESM1-1-CAM5-CMIP5',
# 'CESM1-CAM5-SE-HR',
# 'CESM1-CAM5-SE-LR',
# 'CESM1-WACCM-SC',
# 'CESM2',
# 'CESM2-FV2',
# 'CESM2-WACCM',
# 'CESM2-WACCM-FV2',
# 'CESM2-ssp585-1-0',
# 'CIESM',
# 'CMCC-CM2-HR4',
# 'CMCC-CM2-VHR4',
# 'CNRM-CM6-1',
# 'CNRM-CM6-1-HR',
# 'CNRM-CM6-1-ssp126-1-0',
# 'CNRM-CM6-1-ssp585-1-0',
# 'CNRM-ESM2-1',
# 'CNRM-ESM2-1-ssp585-1-0',
# 'CSIRO-MK3-6-0-rcp85-1-0',
# 'CanESM5',
# 'CanESM5-1',
# 'CanESM5-CanOE',
# 'DCPP-C-amv-1-1',
# 'DCPP-C-ipv-1-1',
# 'E3SM-1-0',
# 'E3SM-1-1',
# 'E3SM-1-1-ECA',
# 'E3SM-2-0',
# 'E3SM-2-0-NARRM',
# 'E3SM-2-1',
# 'EC-Earth3',
# 'EC-Earth3-AerChem',
# 'EC-Earth3-CC',
# 'EC-Earth3-ESM-1',
# 'EC-Earth3-HR',
# 'EC-Earth3-LR',
# 'EC-Earth3-Veg',
# 'EC-Earth3-Veg-LR',
# 'EC-Earth3P',
# 'EC-Earth3P-HR',
# 'EC-Earth3P-VHR',
# 'ECMWF-IFS-HR',
# 'ECMWF-IFS-LR',
# 'ECMWF-IFS-MR',
# 'FGOALS-f3-H',
# 'FGOALS-f3-L',
# 'FGOALS-g3',
# 'GFDL-CM4',
# 'GFDL-ESM2M',
# 'GFDL-ESM4',
# 'GFDL-OM4p5B',
# 'GISS-E2-1-G',
# 'GISS-E2-1-G-CC',
# 'GISS-E2-1-H',
# 'GISS-E2-2-G',
# 'GISS-E2-2-H',
# 'GISS-E3-G',
# 'HadGEM2-ES-rcp85-1-0',
# 'HadGEM3-GC31-HH',
# 'HadGEM3-GC31-HM',
# 'HadGEM3-GC31-LL',
# 'HadGEM3-GC31-LM',
# 'HadGEM3-GC31-MH',
# 'HadGEM3-GC31-MM',
# 'IACETH-SAGE3lambda-3-0-0',
# 'IAMC-AIM-ssp370-1-1',
# 'IAMC-AIM-ssp370-1-1-supplemental-data',
# 'IAMC-AIM-ssp370-lowNTCF-1-1',
# 'IAMC-AIM-ssp370-lowNTCF-1-1-supplemental-data',
# 'IAMC-GCAM4-ssp434-1-1',
# 'IAMC-GCAM4-ssp434-1-1-supplemental-data',
# 'IAMC-GCAM4-ssp460-1-1',
# 'IAMC-GCAM4-ssp460-1-1-supplemental-data',
# 'IAMC-IMAGE-ssp119-1-1',
# 'IAMC-IMAGE-ssp119-1-1-supplemental-data',
# 'IAMC-IMAGE-ssp126-1-1 (40)',
# 'IAMC-IMAGE-ssp126-1-1-supplemental-data',
# 'IAMC-MESSAGE-GLOBIOM-ssp245-1-1',
# 'IAMC-MESSAGE-GLOBIOM-ssp245-1-1-supplemental-data',
# 'IAMC-REMIND-MAGPIE-ssp534-over-1-1',
# 'IAMC-REMIND-MAGPIE-ssp534-over-1-1-supplemental-data',
# 'IAMC-REMIND-MAGPIE-ssp585-1-1',
# 'IAMC-REMIND-MAGPIE-ssp585-1-1-supplemental-data',
# 'INM-CM4-8',
# 'IPSL-CM5A-MR-rcp26-1-0',
# 'IPSL-CM5A-MR-rcp85-1-0',
# 'IPSL-CM5A2-INCA',
# 'IPSL-CM6A-ATM-HR',
# 'IPSL-CM6A-ATM-ICO-HR',
# 'IPSL-CM6A-ATM-ICO-LR',
# 'IPSL-CM6A-ATM-ICO-MR',
# 'IPSL-CM6A-ATM-ICO-VHR',
# 'IPSL-CM6A-ATM-LR-REPROBUS',
# 'IPSL-CM6A-LR',
# 'IPSL-CM6A-LR-INCA',
# 'IPSL-CM6A-MR1',
# 'ImperialCollege-1-1',
# 'ImperialCollege-2-0',
# 'ImperialCollege-AIM-ssp370-1-0',
# 'ImperialCollege-GLOBIOM-ssp245-1-0',
# 'ImperialCollege-IMAGE-ssp119-1-0',
# 'ImperialCollege-IMAGE-ssp126-1-0',
# 'ImperialCollege-REMIND-MAGPIE-ssp534os-1-0',
# 'ImperialCollege-REMIND-MAGPIE-ssp585-1-0',
# 'ImperialCollege-ssp245-covid-4-8-1',
# 'KACE-1-0-G',
# 'KIOST-ESM',
# 'LOCA2--ACCESS-CM2',
# 'LOCA2--ACCESS-ESM1-5',
# 'LOCA2--AWI-CM-1-1-MR',
# 'LOCA2--BCC-CSM2-MR',
# 'LOCA2--CanESM5',
# 'LOCA2--EC-Earth3',
# 'LOCA2--EC-Earth3-Veg',
# 'LOCA2--FGOALS-g3',
# 'LOCA2--GFDL-CM4',
# 'LOCA2--GFDL-ESM4',
# 'LOCA2--INM-CM4-8',
# 'LOCA2--INM-CM5-0',
# 'LOCA2--IPSL-CM6A-LR',
# 'LOCA2--KACE-1-0-G',
# 'LOCA2--MIROC6',
# 'LOCA2--MPI-ESM1-2-HR',
# 'LOCA2--MPI-ESM1-2-LR',
# 'LOCA2--MRI-ESM2-0',
# 'LOCA2--NorESM2-LM',
# 'LOCA2--NorESM2-MM',
# 'LOCA2--TaiESM1',
# 'MCM-UA-1-0',
# 'MIROC-ES2H',
# 'MIROC-ES2L',
# 'MIROC-ESM-CHEM-rcp26-1-0',
# 'MIROC-ESM-CHEM-rcp85-1-0',
# 'MIROC5-rcp26-1-0',
# 'MIROC5-rcp85-1-0',
# 'MIROC6',
# 'MOHC-HadISST-2-2-0-0-0',
# 'MOHC-highresSST-future-1-0-0',
# 'MOHC-highresSST-future-1-0-1',
# 'MPI-B-1pctNdep-1-0',
# 'MPI-ESM1-2-HR',
# 'MPI-ESM1-2-XR',
# 'MPI-M-MACv2-SP-1-0',
# 'MRI-AGCM3-2-H',
# 'MRI-AGCM3-2-S',
# 'MRI-ESM2-0',
# 'MRI-JRA55-do-1-4-0',
# 'MRI-JRA55-do-1-5-0',
# 'NCAR-CCMI-2-0',
# 'NCAR-CCMI-ssp119-1-0',
# 'NCAR-CCMI-ssp126-1-0',
# 'NCAR-CCMI-ssp126-2-0',
# 'NCAR-CCMI-ssp245-1-0',
# 'NCAR-CCMI-ssp245-2-0',
# 'NCAR-CCMI-ssp370-1-0',
# 'NCAR-CCMI-ssp370-2-0',
# 'NCAR-CCMI-ssp434-1-0',
# 'NCAR-CCMI-ssp460-1-0',
# 'NCAR-CCMI-ssp534os-1-0',
# 'NCAR-CCMI-ssp585-1-0',
# 'NCAR-CCMI-ssp585-2-0',
# 'NCAS-2-1-0',
# 'NESM3',
# 'NICAM16-7S',
# 'NICAM16-8S',
# 'NICAM16-9S',
# 'NorCPM1',
# 'NorESM1-F',
# 'NorESM1-M-rcp26-1-0',
# 'NorESM1-M-rcp85-1-0',
# 'NorESM2-LM',
# 'NorESM2-MM',
# 'PCMDI-AMIP-1-1-2',
# 'PCMDI-AMIP-1-1-8',
# 'SAM0-UNICON',
# 'SOLARIS-HEPPA-3-2',
# 'STAR-ESDM-v0--ACCESS-CM2',
# 'STAR-ESDM-v0--ACCESS-ESM1-5',
# 'STAR-ESDM-v0--BCC-CSM2-MR',
# 'STAR-ESDM-v0--CMCC-ESM2',
# 'STAR-ESDM-v0--CanESM5',
# 'STAR-ESDM-v0--FGOALS-g3',
# 'STAR-ESDM-v0--MIROC6',
# 'STAR-ESDM-v0--MPI-ESM1-2-HR',
# 'STAR-ESDM-v0--MPI-ESM1-2-LR',
# 'STAR-ESDM-v0--MRI-ESM2-0',
# 'STAR-ESDM-v0--NESM3',
# 'STAR-ESDM-v0--NorESM2-LM',
# 'STAR-ESDM-v0--NorESM2-MM',
# 'STAR-ESDM-v0--TaiESM1',
# 'UCI-fu-prArctic-prAntarctic-1-0',
# 'UCI-fut2CAntarctic-1-0',
# 'UCI-fut2CArctic-1-0',
# 'UCI-fut2CArctic-2mAntarctic-1-0',
# 'UCI-fut2CBKSeas-1-0',
# 'UCI-fut2COkhotsk-1-0',
# 'UCI-pi-prArctic-prAntarctic-1-1',
# 'UCI-piAntarctic-1-0',
# 'UCI-piArctic-1-0',
# 'UCI-preindustrial-1-0',
# 'UCI-present-1-0',
# 'UCI-present-197901-201412-Arctic-Antarctic-1-0',
# 'UCI-present-197901-201412-clim-Arctic-Antarctic-1-0',
# 'UCI-present-2mAntarctic-1-0',
# 'UColorado-RFMIP-0-4',
# 'UColorado-RFMIP-1-0',
# 'UColorado-RFMIP-1-1',
# 'UColorado-RFMIP-1-2',
# 'UKESM1-0-LL',
# 'UKESM1-0-LL-ssp585-1-0',
# 'UKESM1-1-LL',
# 'UKESM1-ice-LL',
# 'UReading-CCMI-1-0',
# 'UReading-CCMI-ssp119-1-1',
# 'UReading-CCMI-ssp126-1-0',
# 'UReading-CCMI-ssp245-1-0',
# 'UReading-CCMI-ssp370-1-0',
# 'UReading-CCMI-ssp434-1-1',
# 'UReading-CCMI-ssp460-1-1',
# 'UReading-CCMI-ssp534os-1-1',
# 'UReading-CCMI-ssp585-1-0',
# 'UoM-AIM-ssp370-1-2-0',
# 'UoM-AIM-ssp370-1-2-1',
# 'UoM-AIM-ssp370-lowNTCF-1-2-0',
# 'UoM-AIM-ssp370-lowNTCF-1-2-1',
# 'UoM-CMIP-1-2-0',
# 'UoM-GCAM4-ssp434-1-2-0',
# 'UoM-GCAM4-ssp434-1-2-1',
# 'UoM-GCAM4-ssp460-1-2-0',
# 'UoM-GCAM4-ssp460-1-2-1',
# 'UoM-IMAGE-ssp119-1-2-0',
# 'UoM-IMAGE-ssp119-1-2-1',
# 'UoM-IMAGE-ssp126-1-2-0',
# 'UoM-IMAGE-ssp126-1-2-1',
# 'UoM-MESSAGE-GLOBIOM-ssp245-1-2-0',
# 'UoM-MESSAGE-GLOBIOM-ssp245-1-2-1',
# 'UoM-REMIND-MAGPIE-ssp534-over-1-2-0',
# 'UoM-REMIND-MAGPIE-ssp534-over-1-2-1',
# 'UoM-REMIND-MAGPIE-ssp585-1-2-0',
# 'UoM-REMIND-MAGPIE-ssp585-1-2-1',
# 'UoM-ssp126-1-1-0',
# 'UofMD-landState-2-1-h',
# 'UofMD-landState-AIM-ssp370-2-1-f',
# 'UofMD-landState-GCAM-ssp434-2-1-f',
# 'UofMD-landState-GCAM-ssp460-2-1-f',
# 'UofMD-landState-IMAGE-ssp119-2-1-f',
# 'UofMD-landState-IMAGE-ssp126-2-1-e',
# 'UofMD-landState-IMAGE-ssp126-2-1-f',
# 'UofMD-landState-MAGPIE-ssp534-2-1-e',
# 'UofMD-landState-MAGPIE-ssp534-2-1-f',
# 'UofMD-landState-MAGPIE-ssp585-2-1-e',
# 'UofMD-landState-MAGPIE-ssp585-2-1-f',
# 'UofMD-landState-MESSAGE-ssp245-2-1-f',
# 'UofMD-landState-high-2-1-h',
# 'UofMD-landState-low-2-1-h',
# 'VUA-CMIP-BB4CMIP6-1-2',
