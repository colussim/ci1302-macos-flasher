# CI1302 macOS Flasher

[English](README.md) · [Référence des commandes](docs/api/cli.md) · [Dépannage](docs/operations/troubleshooting.md)

Un outil en ligne de commande pour **inspecter, tester la liaison et programmer
les modules vocaux CI1302 depuis un Mac**. Testé sur le **M5Stack Module ASR M147**
avec un Mac Apple Silicon. Il utilise le moteur natif
[citool-cli de coloz](https://github.com/coloz/arduino-ci130x/releases/tag/citool-cli-v1.2.2).
Ce dépôt fournit les scripts, les vérifications et la documentation.

## Démarrage

Il faut macOS, un câble USB de données et le **firmware complet CI1302 FW_V2 au
format `.bin`** fourni par le fabricant ou votre plateforme de génération.
Aucun firmware ni exécutable tiers n'est inclus dans ce dépôt.

```sh
git clone https://github.com/colussim/ci1302-macos-flasher.git
cd ci1302-macos-flasher
./flasher.sh install
./flasher.sh list
./flasher.sh inspect /chemin/firmware.bin
```

L'installation télécharge la version **citool-cli 1.2.2 macOS Universal** et
vérifie les empreintes SHA-256 de l'archive et du logiciel. L'inspection vérifie
les partitions et les CRC du firmware sans ouvrir le port série.

Branchez l'USB-C **du module M147**, en laissant le TAB5 ou autre contrôleur
débranché. Repérez le port CH340 **VID 1A86 / PID 7523** dans la liste. Remplacez
le port d'exemple ci-dessous par le vôtre. Les noms `usbserial` et `wchusbserial`
peuvent désigner le même adaptateur : n'ouvrez pas les deux en même temps.

```sh
./flasher.sh probe /dev/cu.usbserial-110
```

Quand le logiciel affiche `Waiting for a manual device reset into MaskROM...`,
appuyez une fois sur **Debug Rst**. Ce test charge un agent en RAM **sans effacer
ni écrire la mémoire Flash**. Il change l'état du module ; faites ensuite un
reset ou une remise sous tension. Continuez seulement si le test de liaison
réussit.

```sh
./flasher.sh flash /dev/cu.usbserial-110 /chemin/firmware.bin
```

Attendez le message MaskROM et appuyez **à nouveau sur Debug Rst**. Gardez le
câble branché. Le flash écrit le firmware complet et vérifie son CRC. Il faut
obtenir l'écriture et la vérification à **100 %**, le message
`Flash completed; firmware CRC verification passed.` et un code de sortie zéro.
Redémarrez ensuite le module et testez votre mot de réveil et ses événements UART.

Si vous disposez de l'empreinte SHA-256 fournie par le fabricant :

```sh
./flasher.sh flash /dev/cu.usbserial-110 /chemin/firmware.bin \
  --sha256 EMPREINTE_SHA256_DE_64_CARACTERES
```

## Ce qui a été testé

Le 7 octobre 2026, une image SmartPI FW_V2 de **1 638 005 octets** a été écrite
sur un M147 puis vérifiée par CRC en **115,94 secondes**, sur Mac Apple Silicon
avec macOS 27.0.1. Les vitesses utilisées étaient **115200 / 460800 / 230400 bauds**
pour la connexion, l'agent et le firmware.

Le succès du flash ne prouve pas la reconnaissance du mot de réveil. Cette
reconnaissance et la communication avec votre contrôleur se testent séparément.
Les Mac Intel et les autres cartes CI1302 n'ont pas été validés physiquement
ici. Le script accepte uniquement le CI1302 et les interfaces CH340 1A86:7523 ;
il rejette les CI1303/CI1306 et les ports USB CDC du TAB5.

Conservez le firmware complet d'origine avant de remplacer celui du module.
Ce dépôt ne programme pas l'ESP32, ne génère pas le mot de réveil et n'accepte
pas un fichier de modèle vocal ou un paquet OTA comme firmware complet.

Les [notes M147](docs/operations/m147.md) expliquent les DIP. La documentation
technique détaillée et les messages du script sont en anglais.

Auteur : **Emmanuel COLUSSI**. Scripts et documentation originale sous
[licence MIT](LICENSE). Le moteur `citool-cli` appartient à ses mainteneurs ;
consultez les [crédits et notices](THIRD_PARTY_NOTICES.md).
