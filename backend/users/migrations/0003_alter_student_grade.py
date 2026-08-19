from django.db import migrations, models
import django.db.models.deletion


def clear_old_grades(apps, schema_editor):
    Student = apps.get_model("users", "Student")
    Student.objects.all().update(grade=None)


class Migration(migrations.Migration):

    dependencies = [
        (
            "courses",
            "0002_grade_alter_chapter_options_alter_topic_options_and_more",
        ),
        ("users", "0002_alter_student_grade"),
    ]

    operations = [
        migrations.RunPython(
            clear_old_grades,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="student",
            name="grade",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="students",
                to="courses.grade",
            ),
        ),
    ]