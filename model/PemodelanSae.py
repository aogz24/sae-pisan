class PemodelanSae:
    def __init__(self, variabel_independen, variabel_dependen):
        self._variabel_independen = variabel_independen
        self._variabel_dependen = variabel_dependen
        self._hasil_sae = None
        self._var_sae = None

    @property
    def variabel_independen(self):
        return self._variabel_independen

    @variabel_independen.setter
    def variabel_independen(self, value):
        self._variabel_independen = value

    @property
    def variabel_dependen(self):
        return self._variabel_dependen

    @variabel_dependen.setter
    def variabel_dependen(self, value):
        self._variabel_dependen = value

    @property
    def hasil_sae(self):
        return self._hasil_sae

    @hasil_sae.setter
    def hasil_sae(self, value):
        self._hasil_sae = value

    @property
    def var_sae(self):
        return self._var_sae

    @var_sae.setter
    def var_sae(self, value):
        self._var_sae = value
    
    def __str__(self):
        return (f'PemodelanSae(variabel_independen={self._variabel_independen}, '
                f'variabel_dependen={self._variabel_dependen}, '
                f'hasil_sae={self._hasil_sae}, var_sae={self._var_sae})')