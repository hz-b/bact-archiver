import unittest
import bact_archiver.config


class LoadConfig(unittest.TestCase):

    mod_name = "bact_archiver"

    def test001_LoadConfigurationFile(self):
        """Test that the archiver configuration file is fonnd"""
        filename = bact_archiver.config.get_config_filename(self.mod_name)
        self.assertIsNotNone(filename)

    def test002_LoadConfiguration(self):
        """Test that the archiver configurations are loaded"""
        bact_archiver.config.archiver_configurations(self.mod_name)

    def test003_LoadConfiguration(self):
        """Test that the archiver configurations have a name"""
        tmp = bact_archiver.config.archiver_configurations(self.mod_name)
        for name, archiver in tmp.items():
            self.assertIsNotNone(archiver.name)

    def test004_LoadConfiguration(self):
        """Test that the archiver configurations are printable"""
        tmp = bact_archiver.config.archiver_configurations(self.mod_name)
        for name, archiver in tmp.items():
            str(archiver)
            repr(archiver)

    def test010_ModuleInsertConfigurations(self):
        """Test that the archiver configurations are inserted as archivers in
        the archiver module
        """

        import bact_archiver.archiver
        import bact_archiver.register

        configs = bact_archiver.config.archiver_configurations(self.mod_name)
        bact_archiver.register.add_archivers_to_module(self.mod_name, configs)

    def test020_AutomaticLoadDefault(self):
        import bact_archiver

        default_archiver = bact_archiver.default
        assert default_archiver

    def test021_AutomaticLoadDefaultName(self):
        import bact_archiver

        default_archiver = bact_archiver.default
        default_archiver.name

    def test022_AutomaticLoadDefaultName(self):
        import bact_archiver

        default_archiver = bact_archiver.default
        default_archiver.description


if __name__ == "__main__":
    unittest.main()
