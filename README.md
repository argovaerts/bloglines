<div align="center">
    <h1>bloglines</h1>
    <p><a href="https://codeberg.org/argovaerts/bloglines">Codeberg</a> | <a href="https://github.com/argovaerts/bloglines">Github</a> (mirror)
</div>

**Bloglines** is a simple Python based tool for making and uploading a simple website or blog.

## Demo
* See [apg.im](https://apg.im)

## Usage

### 1. Make a new post
```
python bloglines.py new [<type>]
```
Default type is `note`.

### 2. (Re)build the blog
```
python bloglines.py make [<output_dir>]
```
Default directory is `output/`.

### 2. Upload the blog with FTP
```
python bloglines.py upload [<output_dir>]
```
Default directory is `output/`.

Requires the following environment variables to be set (can be in .env file):
* `FTP_SECURE`
* `FTP_SERVER`
* `FTP_USERNAME`
* `FTP_PASSWORD`

See also: .env.template

## Third party libraries
* See [LIBRARIES](LIBRARIES.md) file

## License
* See [LICENSE](LICENSE.md) file

## Version
* Version 0.0.1

## Contact
* Arne Govaerts
* [apg.im](https://apg.im)
* <a@apg.im>

