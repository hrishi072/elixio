from django import forms

from .models import Board


class BoardForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))
    cover = forms.ImageField(
        widget=forms.FileInput(),
        required=False
    )

    class Meta:
        model = Board
        fields = ('title', 'description', 'cover')
