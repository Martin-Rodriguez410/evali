from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registros', '0002_alter_madre_rut_alter_parto_fecha_hora_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reciennacido',
            name='talla',
            field=models.DecimalField(decimal_places=1, max_digits=4),
        ),
    ]
