from data_process.astrid_2020.auth import auth_dict
from delphin_6_automation.database_interactions import mongo_setup
from delphin_6_automation.database_interactions.db_templates import delphin_entry, sample_entry


def delete_duplicate_designs():
    print('Getting design files')
    designs = delphin_entry.Design.objects()
    duplicates = []
    for design in designs:
        if design.design_name.endswith("SD00"):
            print(f'Downloading design: {design.design_name}')
            duplicates.append(design.design_name)
            #design.delete()

    print(f'Extra designs: {len(duplicates)}')

    return duplicates


def clean_strategy(duplicates):
    print('\nLooking in Strategy')
    strategy_doc = sample_entry.Strategy.objects().first()

    correct_designs = []
    for index, design in enumerate(strategy_doc.strategy['design']):
        if design not in duplicates:
            correct_designs.append(design)

    print(f'Keeping {len(correct_designs)} in strategy')
    new_strategy = strategy_doc.strategy
    new_strategy['design'] = correct_designs
    strategy_doc.strategy = new_strategy
    strategy_doc.save()


if __name__ == '__main__':
    server = mongo_setup.global_init(auth_dict)

    duplicates_ = delete_duplicate_designs()
    clean_strategy(duplicates_)

    mongo_setup.global_end_ssh(server)
