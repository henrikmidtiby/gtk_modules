# gtk_modules

gtk_modules is a collection of classes with common used GTK3 things.

## Getting Started Ubuntu

### Prerequisites

* python 3 and pip
* PyGObject

### Installation

* Open a terminal in the folder where gtk_modules shall be.
* Clone the repository:  `git clone git@gitlab.com:UAS-centre/gtk_modules.git`
* Install: `pip install .`

## Usage

```
from gtk_modules import Menu, Video, VideoDrawHandler, Mouse ...
from gtk_modules.dialogs import FileDialog, Dialog ...

video = Video()
mouse = Mouse(event_box)
...
```

## Author

Written by Henrik Dyrberg Egemose (hesc@mmmi.sdu.dk) as part of the InvaDrone and Back2Nature projects, research projects by the University of Southern Denmark UAS Center (SDU UAS Center).

## License

This project is licensed under the 3-Clause BSD License - see the [LICENSE](LICENSE) file for details.
