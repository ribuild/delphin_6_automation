__author__ = "Christian Kongsgaard"
__license__ = 'MIT'

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules

# RiBuild Modules
from delphin_6_automation.database_interactions.db_templates import delphin_entry
from delphin_6_automation.database_interactions.db_templates import sample_entry
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.auth import auth_dict

# -------------------------------------------------------------------------------------------------------------------- #
# RIBuild


def correct_delphin():

    samples = sample_entry.Sample.objects().only('delphin_docs')
    print(f'There is {samples.count()} samples in DB')

    sample_projects = []
    for sample in samples:
        if len(sample.delphin_docs) == 0:
            print(f'Sample {sample.id} has no delphin projects. Deleting!')
            sample.delete()
        else:
            for delphin in sample.delphin_docs:
                sample_projects.append(delphin.id)

    print(f'There is {len(sample_projects)} connected to a sample')

    projects = delphin_entry.Delphin.objects().only('id')

    print(f'There are currently {len(projects)} projects in the database')

    print('Starting')
    for proj in projects:
        if proj.id not in sample_projects:
            #print(f'Project with ID: {proj.id} is not part of a sample!')
            proj.delete()


def correct_sample():
    samples = sample_entry.Sample.objects()

    for sample in samples:
        docs = []
        for ref in sample.delphin_docs:
            delphin_projects = delphin_entry.Delphin.objects(id=ref.id)
            if delphin_projects:
                docs.append(delphin_projects.first())
            else:
                print(f'Found non existent project: {ref.id}')

        sample.delphin_docs = docs
        sample.save()


def correct_strategy():
    strategy = sample_entry.Strategy.objects().first()
    keep = []
    for sample in strategy.samples:
        found_sample = sample_entry.Sample.objects(id=sample.id)
        if found_sample:
            keep.append(found_sample.first().id)
        else:
            print(f"Sample {sample.id} was not in the DB")

    print(f"Found samples {len(keep)} to keep: {keep}")
    strategy.samples = keep
    strategy.save()


def modify_sample():
    id_ = "5e7878ce582e3e000172996d"
    sample = sample_entry.Sample.objects(id=id_).first()
    print('Got sample')
    sample.mean = {}
    sample.standard_deviation = {}
    sample.save()


def correct_sample2():
    samples = sample_entry.Sample.objects().only('id')
    print(f"There is {samples.count()} samples in DB")

    for i in range(samples.count()):
        samples = sample_entry.Sample.objects(iteration=i).only('id')
        print(f'There is {samples.count()} with iteration {i}')

        if samples.count() > 1:
            print(f"There is {samples.count()} samples with iteration {i}")
            for j, sample in enumerate(samples):
                if j == 0:
                    pass
                else:
                    print(f'Deleting: {sample.id}')
                    #sample.delete()

if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)
    #modify_sample()
    #correct_sample()
    #correct_sample2()
    correct_delphin()
    correct_strategy()
    mongo_setup.global_end_ssh(server)




