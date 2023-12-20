from pin_maker import db_tools, space_tools, pinterest
import io
import csv
from datetime import datetime


def main():
    pins = db_tools.get_pins_for_day()
    pins = space_tools.prepare_pins(pins)

    chunks = []
    chunk = []

    for pin in pins:
        if len(chunk) == 199:
            chunks.append(chunk)
            chunk = []
        chunk.append(pin)
    if chunk:
        chunks.append(chunk)
    csv_keys = []
    
    for i, part_of_pins in enumerate(chunks):
        with io.StringIO() as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Title', 'Media URL', 'Pinterest board', 'Description', 'Link', 'Keywords'])
            for pin in part_of_pins:
                writer.writerow([
                    pin.title,
                    pin.media_url,
                    pin.board,
                    pin.description,
                    pin.link,
                    pin.key_words,
                ])
            csv_file.seek(0)
            csv_keys.append(space_tools.save_to_space(
                csv_file.getvalue(),
                'csv',
                f'pins_{int(datetime.now().timestamp())}_{i}.csv'
            ))
    csv_links = [space_tools.get_s3_link(key) for key in csv_keys]
    is_succesful = pinterest.upload_csv(csv_links)
    if is_succesful:
        db_tools.mark_pins_as_done(pins)


if __name__ == '__main__':
    main()