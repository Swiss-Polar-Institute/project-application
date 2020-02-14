from django.db import models


class Colour(models.Model):
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    name = models.CharField(max_length=64, help_text='Name of the colour', unique=True)
    hex_code = models.CharField(max_length=7, help_text='Hex code, e.g. FF0000 for red', unique=True)

    def __str__(self):
        return self.name


class ColourPair(models.Model):
    objects = models.Manager()  # Helps Pycharm CE auto-completion

    description = models.CharField(max_length=128,
                                   help_text='For example "Red background with grey text" or "Use for alerts"',
                                   unique=True)
    background = models.ForeignKey(Colour, on_delete=models.PROTECT, related_name='colorpair_background')
    text = models.ForeignKey(Colour, on_delete=models.PROTECT, related_name='colorpair_text')

    def __str__(self):
        return self.description