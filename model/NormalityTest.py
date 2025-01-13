class NormalityTest:
    def __init__(self, data, grafik, jenis_test):
        self.data = data
        self.grafik = grafik
        self.jenis_test = jenis_test

    def run_test(self):
        # Perform normality test based on jenis_test
        if self.jenis_test == "Shapiro-Wilk":
            # Perform Shapiro-Wilk test
            pass
        elif self.jenis_test == "Jarque-Bera":
            # Perform Jarque-Bera test
            pass
        elif self.jenis_test == "Uji Lilliefors":
            # Perform Uji Lilliefors test
            pass
        else:
            # Handle invalid jenis_test value

    def generate_graph(self):
        # Generate graph based on grafik
        if self.grafik == "qq plot":
            # Generate qq plot
            pass
        elif self.grafik == "histogram":
            # Generate histogram
            pass
        elif self.grafik == "both":
            # Generate both qq plot and histogram
            pass
        else:
            # Handle invalid grafik value
            pass