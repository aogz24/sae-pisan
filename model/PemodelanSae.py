class PemodelanSae:
    def __init__(self, variabel_independen, variabel_dependen):
        self._variabel_independen = variabel_independen
        self._variabel_dependen = variabel_dependen
        self._hasil_sae = None
        self._var_sae = None

    @property
    def getVariabelIndependen(self):
        return self._variabel_independen

    @getVariabelIndependen.setter
    def setVariabelIndependen(self, value):
        self._variabel_independen = value

    @property
    def getVariabelDependen(self):
        return self._variabel_dependen

    @getVariabelDependen.setter
    def setVariabelDependen(self, value):
        self._variabel_dependen = value

    @property
    def getHasilSae(self):
        return self._hasil_sae

    @getHasilSae.setter
    def setHasilSae(self, value):
        self._hasil_sae = value

    @property
    def getVarSae(self):
        return self._var_sae

    @getVarSae.setter
    def setVarSae(self, value):
        self._var_sae = value
    
    def __str__(self):
        return (f'PemodelanSae(variabel_independen={self._variabel_independen}, '
                f'variabel_dependen={self._variabel_dependen}, '
                f'hasil_sae={self._hasil_sae}, var_sae={self._var_sae})')