from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('queues', '0003_alter_queue_token_number'),
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='doctor',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='appointments.doctor'),
        ),
    ]
