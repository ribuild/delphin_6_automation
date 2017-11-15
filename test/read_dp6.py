import delphin_6_automation.delphin_db as de

folder_path = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\dephin_6_templates'
template0 = 'template_0.d6p'

a = de.dp6_to_dict(folder_path + '/' + template0)
print(a)