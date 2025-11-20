from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beds', '0002_remove_bed_hospital_remove_bed_is_occupied_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bed',
            name='hospital',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='hospitals.hospital'),
        ),
    ]
