import sqlite3
import datetime
import re
import subprocess
import urllib.parse
import os
import time
import shutil
import fnmatch
import json
import coloredlogs, logging

# Create a logger object.
logger = logging.getLogger("bear")
coloredlogs.install(level='DEBUG')

class BearSync:
    def __init__(self):
        self.make_tag_folders = True  # Exports to folders using first tag only, if `multi_tag_folders = False`
        self.multi_tag_folders = False  # Copies notes to all 'tag-paths' found in note!
        # Only active if `make_tag_folders = True`
        self.hide_tags_in_comment_block = (
            True  # Hide tags in HTML comments: `<!-- #mytag -->`
        )

        # The following two lists are more or less mutually exclusive, so use only one of them.
        # (You can use both if you have some nested tags where that makes sense)
        # Also, they only work if `make_tag_folders = True`.
        self.only_export_these_tags = (
            []
        )  # Leave this list empty for all notes! See below for sample
        # only_export_these_tags = ['bear/github', 'writings']
        self.no_export_tags = (
            []
        )  # If a tag in note matches one in this list, it will not be exported.
        # no_export_tags = ['private', '.inbox', 'love letters', 'banking']

        self.export_as_textbundles = (
            False  # Exports as Textbundles with images included
        )
        self.export_as_hybrids = (
            True  # Exports as .textbundle only if images included, otherwise as .md
        )
        # Only used if `export_as_textbundles = True`
        self.export_image_repository = True  # Export all notes as md but link images to
        # a common repository exported to: `assets_path`
        # Only used if `export_as_textbundles = False`

        self.my_sync_service = "Dropbox"  # Change 'Dropbox' to 'Box', 'Onedrive',
        # or whatever folder of sync service you need.

        # NOTE! Your user 'HOME' path and '/BearNotes' is added below!
        # NOTE! So do not change anything below here!!!

        self.HOME = os.getenv("HOME", "")

        self.set_logging_on = True

        # NOTE! if 'BearNotes' is left blank, all other files in my_sync_service will be deleted!!
        self.export_path = os.path.join(self.HOME, "BearNotes")
        # NOTE! "export_path" is used for sync-back to Bear, so don't change this variable name!
        self.multi_export = [(self.export_path, True)]  # only one folder output here.
        # Use if you want export to severa places like: Dropbox and OneDrive, etc. See below
        # Sample for multi folder export:
        # export_path_aux1 = os.path.join(HOME, 'OneDrive', 'BearNotes')
        # export_path_aux2 = os.path.join(HOME, 'Box', 'BearNotes')

        # NOTE! All files in export path not in Bear will be deleted if delete flag is "True"!
        # Set this flag fo False only for folders to keep old deleted versions of notes
        # multi_export = [(export_path, True), (export_path_aux1, False), (export_path_aux2, True)]

        self.temp_path = os.path.join(
            self.HOME, "Temp", "BearExportTemp"
        )  # NOTE! Do not change the "BearExportTemp" folder name!!!
        self.bear_db = os.path.join(
            self.HOME,
            "Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite",
        )
        self.sync_backup = os.path.join(
            self.HOME, "BearSyncBackup"
        )  # Backup of original note before sync to Bear.
        self.log_file = os.path.join(self.sync_backup, "bear_export_sync_log.txt")

        # Paths used in image exports:
        self.bear_image_path = os.path.join(
            self.HOME,
            "Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/Local Files/Note Images",
        )
        self.assets_path = os.path.join(self.HOME, self.export_path, "BearImages")

        self.sync_ts = ".sync-time.log"
        self.export_ts = ".export-time.log"

        self.sync_ts_file = os.path.join(self.export_path, self.sync_ts)
        self.sync_ts_file_temp = os.path.join(self.temp_path, self.sync_ts)
        self.export_ts_file_exp = os.path.join(self.export_path, self.export_ts)
        self.export_ts_file = os.path.join(self.temp_path, self.export_ts)

        self.gettag_sh = os.path.join(self.HOME, "temp/gettag.sh")
        self.gettag_txt = os.path.join(self.HOME, "temp/gettag.txt")

        self.code_blocks = re.compile(r"^`{3}([\S]+)?\n([\s\S]+)\n`{3}", re.IGNORECASE)

    def sync(self):
        self.init_gettag_script()
        logger.debug("Syncing MD updates")
        self.sync_md_updates()
        if self.check_db_modified():
            logger.debug("Deleting old temp files")
            self.delete_old_temp_files()
            logger.debug("Exporting files")
            note_count = self.export_markdown()
            logger.debug(f"Exported {note_count} files")
            self.write_time_stamp()
            logger.debug(f"Syncing files from temp")
            self.rsync_files_from_temp()
            if self.export_image_repository and not self.export_as_textbundles:
                self.copy_bear_images()
            # notify('Export completed')
            logger.debug(f"{note_count} notes exported to: {self.export_path}")
            self.write_log(str(note_count) + " notes exported to: " + self.export_path)
        else:
            logger.debug("No changes found")

    def write_log(self, message):
        if self.set_logging_on == True:
            if not os.path.exists(self.sync_backup):
                os.makedirs(self.sync_backup)
            time_stamp = datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S")
            message = message.replace(self.export_path + "/", "")
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(time_stamp + ": " + message + "\n")

    def check_db_modified(self):
        if not os.path.exists(self.sync_ts_file):
            return True
        db_ts = self.get_file_date(self.bear_db)
        last_export_ts = self.get_file_date(self.export_ts_file_exp)
        return db_ts > last_export_ts

    def export_markdown(self):
        with sqlite3.connect(self.bear_db) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM `ZSFNOTE` WHERE `ZTRASHED` LIKE '0'"
            c = conn.execute(query)
        note_count = 0
        for row in c:
            title = row["ZTITLE"]
            md_text = row["ZTEXT"].rstrip()
            creation_date = row["ZCREATIONDATE"]
            modified = row["ZMODIFICATIONDATE"]
            uuid = row["ZUNIQUEIDENTIFIER"]
            filename = self.clean_title(title)  # + date_time_conv(creation_date)
            file_list = []
            if self.make_tag_folders:
                file_list = self.sub_path_from_tag(self.temp_path, filename, md_text)
            else:
                file_list.append(os.path.join(self.temp_path, filename))
            if file_list:
                mod_dt = self.dt_conv(modified)
                md_text = self.hide_tags(md_text)
                md_text += "\n\n<!-- {BearID:" + uuid + "} -->\n"
                for filepath in file_list:
                    note_count += 1
                    # print(filepath)
                    if self.export_as_textbundles:
                        if self.check_image_hybrid(md_text):
                            self.make_text_bundle(md_text, filepath, mod_dt)
                        else:
                            self.write_file(filepath + ".md", md_text, mod_dt)
                    elif self.export_image_repository:
                        md_proc_text = self.process_image_links(md_text, filepath)
                        self.write_file(filepath + ".md", md_proc_text, mod_dt)
                    else:
                        self.write_file(filepath + ".md", md_text, mod_dt)
        return note_count

    def check_image_hybrid(self, md_text):
        if self.export_as_hybrids:
            if re.search(r"\[image:(.+?)\]", md_text):
                return True
            else:
                return False
        else:
            return True

    def make_text_bundle(self, md_text, filepath, mod_dt):
        """
        Exports as Textbundles with images included 
        """
        bundle_path = filepath + ".textbundle"
        assets_path = os.path.join(bundle_path, "assets")
        if not os.path.exists(bundle_path):
            os.makedirs(bundle_path)
            os.makedirs(assets_path)

        info = """{
        "transient" : true,
        "type" : "net.daringfireball.markdown",
        "creatorIdentifier" : "net.shinyfrog.bear",
        "version" : 2
        }"""
        matches = re.findall(r"\[image:(.+?)\]", md_text)
        for match in matches:
            image_name = match
            new_name = image_name.replace("/", "_")
            source = os.path.join(self.bear_image_path, image_name)
            target = os.path.join(self.assets_path, new_name)
            shutil.copy2(source, target)

        md_text = re.sub(r"\[image:(.+?)/(.+?)\]", r"![](assets/\1_\2)", md_text)
        self.write_file(bundle_path + "/text.md", md_text, mod_dt)
        self.write_file(bundle_path + "/info.json", info, mod_dt)
        os.utime(bundle_path, (-1, mod_dt))

    def sub_path_from_tag(self, temp_path, filename, md_text):
        # md_text = code_blocks.sub("", md_text)
        # Get tags in note:
        pattern1 = r"(?<!\S)\#([.\w\/\-]+)[ \n]?(?!([\/ \w]+\w[#]))"
        pattern2 = r"(?<![\S])\#([^ \d][.\w\/ ]+?)\#([ \n]|$)"
        if self.multi_tag_folders:
            # Files copied to all tag-folders found in note
            tags = []
            for matches in re.findall(pattern1, md_text):
                tag = matches[0]
                tags.append(tag)
            for matches2 in re.findall(pattern2, md_text):
                tag2 = matches2[0]
                tags.append(tag2)
            if len(tags) == 0:
                # No tags found, copy to root level only
                return [os.path.join(self.temp_path, filename)]
        else:
            # Only folder for first tag
            match1 = re.search(pattern1, md_text)
            match2 = re.search(pattern2, md_text)
            if match1 and match2:
                if match1.start(1) < match2.start(1):
                    tag = match1.group(1)
                else:
                    tag = match2.group(1)
            elif match1:
                tag = match1.group(1)
            elif match2:
                tag = match2.group(1)
            else:
                # No tags found, copy to root level only
                return [os.path.join(self.temp_path, filename)]
            tags = [tag]
        paths = []
        for tag in tags:
            if tag == "/":
                continue
            if self.only_export_these_tags:
                export = False
                for export_tag in self.only_export_these_tags:
                    if tag.lower().startswith(export_tag.lower()):
                        export = True
                        break
                if not export:
                    continue
            for no_tag in self.no_export_tags:
                if tag.lower().startswith(no_tag.lower()):
                    return []
            if tag.startswith("."):
                # Avoid hidden path if it starts with a '.'
                sub_path = "_" + tag[1:]
            else:
                sub_path = tag
            tag_path = os.path.join(self.temp_path, sub_path)
            if not os.path.exists(tag_path):
                os.makedirs(tag_path)
            paths.append(os.path.join(tag_path, filename))
        return paths

    def process_image_links(self, md_text, filepath):
        """
        Bear image links converted to MD links
        """
        root = filepath.replace(self.temp_path, "")
        level = len(root.split("/")) - 2
        parent = "../" * level
        md_text = re.sub(
            r"\[image:(.+?)\]", r"![](" + parent + r"BearImages/\1)", md_text
        )
        return md_text

    def restore_image_links(self, md_text):
        """
        MD image links restored back to Bear links
        """
        # if not re.search(r'!\[.*?\]\(assets/.+?\)', md_text):
        #     # No image links in note, return unchanged:
        #     print("No image links found")
        #     return md_text
        if self.export_as_textbundles:
            md_text = re.sub(
                r'!\[(.*?)\]\(assets/(.+?)_(.+?)( ".+?")?\) ?',
                r"[image:\2/\3]\4 \1",
                md_text,
            )
        elif self.export_image_repository:
            # md_text = re.sub(r'\[image:(.+?)\]', r'![](../assets/\1)', md_text)
            print("Found image")
            md_text = re.sub(
                r"!\[\]\((\.\./)*BearImages/(.+?)\)", r"[image:\2]", md_text
            )
            print(md_text)
        return md_text

    def copy_bear_images(self):
        # Image files copied to a common image repository
        subprocess.call(
            [
                "rsync",
                "-r",
                "-t",
                "--delete",
                self.bear_image_path + "/",
                self.assets_path,
            ]
        )

    def write_time_stamp(self):
        # write to time-stamp.txt file (used during sync)
        self.write_file(
            self.export_ts_file,
            "Markdown from Bear written at: "
            + datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S"),
            0,
        )
        self.write_file(
            self.sync_ts_file_temp,
            "Markdown from Bear written at: "
            + datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S"),
            0,
        )

    def hide_tags(self, md_text):
        # Hide tags from being seen as H1, by placing `period+space` at start of line:
        if self.hide_tags_in_comment_block:
            md_text = re.sub(r"(\n)[ \t]*(\#[\w.].+)", r"\1<!-- \2 -->", md_text)
        else:
            md_text = re.sub(r"(\n)[ \t]*(\#[\w.]+)", r"\1. \2", md_text)
        return md_text

    def restore_tags(self, md_text):
        # Tags back to normal Bear tags, stripping the `period+space` at start of line:
        # if hide_tags_in_comment_block:
        md_text = re.sub(r"(\n)<!--[ \t]*(\#[\w.].+?) -->", r"\1\2", md_text)
        # else:
        md_text = re.sub(r"(\n)\.[ \t]*(\#[\w.]+)", r"\1\2", md_text)
        return md_text

    def clean_title(self, title):
        title = title[:56].strip()
        if title == "":
            title = "Untitled"
        title = re.sub(r"[/\\*?$@!^&\|~:]", r"-", title)
        title = re.sub(r"-$", r"", title)
        return title.strip()

    def write_file(self, filename, file_content, modified):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(file_content)
        if modified > 0:
            os.utime(filename, (-1, modified))

    def read_file(self, file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            file_content = f.read()
        return file_content

    def get_file_date(self, filename):
        try:
            t = os.path.getmtime(filename)
            return t
        except:
            return 0

    def dt_conv(self, dtnum):
        # Formula for date offset based on trial and error:
        hour = 3600  # seconds
        year = 365.25 * 24 * hour
        offset = year * 31 + hour * 6
        return dtnum + offset

    def date_time_conv(self, dtnum):
        newnum = dt_conv(dtnum)
        dtdate = datetime.datetime.fromtimestamp(newnum)
        # print(newnum, dtdate)
        return dtdate.strftime(" - %Y-%m-%d_%H%M")

    def time_stamp_ts(self, ts):
        dtdate = datetime.datetime.fromtimestamp(ts)
        return dtdate.strftime("%Y-%m-%d at %H:%M")

    def date_conv(self, dtnum):
        dtdate = datetime.datetime.fromtimestamp(dtnum)
        return dtdate.strftime("%Y-%m-%d")

    def delete_old_temp_files(self):
        # Deletes all files in temp folder before new export using "shutil.rmtree()":
        # NOTE! CAUTION! Do not change this function unless you really know shutil.rmtree() well!
        if os.path.exists(self.temp_path) and "BearExportTemp" in self.temp_path:
            # *** NOTE! Double checking that temp_path folder actually contains "BearExportTemp"
            # *** Because if temp_path is accidentally empty or root,
            # *** shutil.rmtree() will delete all files on your complete Hard Drive ;(
            shutil.rmtree(self.temp_path)
            # *** NOTE: USE rmtree() WITH EXTREME CAUTION!
        os.makedirs(self.temp_path)

    def rsync_files_from_temp(self):
        # Moves markdown files to new folder using rsync:
        # This is a very important step!
        # By first exporting all Bear notes to an emptied temp folder,
        # rsync will only update destination if modified or size have changed.
        # So only changed notes will be synced by Dropbox or OneDrive destinations.
        # Rsync will also delete notes on destination if deleted in Bear.
        # So doing it this way saves a lot of otherwise very complex programing.
        # Thank you very much, Rsync! ;)
        for (dest_path, delete) in self.multi_export:
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            if delete:
                subprocess.call(
                    [
                        "rsync",
                        "-r",
                        "-t",
                        "--delete",
                        "--exclude",
                        "BearImages/",
                        "--exclude",
                        ".Ulysses*",
                        "--exclude",
                        "*.Ulysses_Public_Filter",
                        self.temp_path + "/",
                        dest_path,
                    ]
                )
            else:
                subprocess.call(
                    ["rsync", "-r", "-t", self.temp_path + "/", dest_path]
                )

    def sync_md_updates(self):
        updates_found = False
        if not os.path.exists(self.sync_ts_file) or not os.path.exists(
            self.export_ts_file
        ):
            return False
        ts_last_sync = os.path.getmtime(self.sync_ts_file)
        ts_last_export = os.path.getmtime(self.export_ts_file)
        # Update synced timestamp file:
        self.update_sync_time_file(0)
        file_types = ("*.md", "*.txt", "*.markdown")
        for (root, dirnames, filenames) in os.walk(self.export_path):
            """
            This step walks down into all sub folders, if any.
            """
            for pattern in file_types:
                for filename in fnmatch.filter(filenames, pattern):
                    md_file = os.path.join(root, filename)
                    ts = os.path.getmtime(md_file)
                    if ts > ts_last_sync:
                        if not updates_found:  # Yet
                            # Wait 5 sec at first for external files to finish downloading from dropbox.
                            # Otherwise images in textbundles might be missing in import:
                            time.sleep(5)
                        updates_found = True
                        md_text = read_file(md_file)
                        backup_ext_note(md_file)
                        if check_if_image_added(md_text, md_file):
                            textbundle_to_bear(md_text, md_file, ts)
                            write_log("Imported to Bear: " + md_file)
                        else:
                            update_bear_note(md_text, md_file, ts, ts_last_export)
                            write_log("Bear Note Updated: " + md_file)
        if updates_found:
            # Give Bear time to process updates:
            time.sleep(3)
            # Check again, just in case new updates synced from remote (OneDrive/Dropbox)
            # during this process!
            # The logic is not 100% fool proof, but should be close to 99.99%
            self.sync_md_updates()  # Recursive call
        return updates_found

    def check_if_image_added(self, md_text, md_file):
        # if not '.textbundle/' in md_file:
        #     return False
        matches = re.findall(r"!\[.*?\]\(assets/(.+?_).+?\)", md_text)
        for image_match in matches:
            if not re.match(
                r"[0-9A-F]{8}-([0-9A-F]{4}-){3}[0-9A-F]{12}-[0-9A-F]{3,5}-[0-9A-F]{16}_",
                image_match,
            ):
                return True
        return False

    def textbundle_to_bear(self, md_text, md_file, mod_dt):
        md_text = self.restore_tags(md_text)
        bundle = os.path.split(md_file)[0]
        match = re.search(r"\{BearID:(.+?)\}", md_text)
        if match:
            uuid = match.group(1)
            # Remove old BearID: from new note
            md_text = (
                re.sub(r"\<\!-- ?\{BearID\:" + uuid + r"\} ?--\>", "", md_text).rstrip()
                + "\n"
            )
            md_text = insert_link_top_note(
                md_text, "Images added! Link to original note: ", uuid
            )
        else:
            # New textbundle (with images), add path as tag:
            md_text = get_tag_from_path(md_text, bundle, self.export_path)
        write_file(md_file, md_text, mod_dt)
        os.utime(bundle, (-1, mod_dt))
        subprocess.call(["open", "-a", "/applications/bear.app", bundle])
        time.sleep(0.5)

    def backup_ext_note(self, md_file):
        if ".textbundle" in md_file:
            bundle_path = os.path.split(md_file)[0]
            bundle_name = os.path.split(bundle_path)[1]
            target = os.path.join(sync_backup, bundle_name)
            bundle_raw = os.path.splitext(target)[0]
            count = 2
            while os.path.exists(target):
                # Adding sequence number to identical filenames, preventing overwrite:
                target = bundle_raw + " - " + str(count).zfill(2) + ".textbundle"
                count += 1
            shutil.copytree(bundle_path, target)
        else:
            # Overwrite former bacups of incoming changes, only keeps last one:
            shutil.copy2(md_file, sync_backup + "/")

    def update_sync_time_file(self, ts):
        self.write_file(
            self.sync_ts_file,
            "Checked for Markdown updates to sync at: "
            + datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S"),
            ts,
        )

    def update_bear_note(self, md_text, md_file, ts, ts_last_export):
        md_text = self.restore_tags(md_text)
        md_text = self.restore_image_links(md_text)
        uuid = ""
        match = re.search(r"\{BearID:(.+?)\}", md_text)
        sync_conflict = False
        if match:
            uuid = match.group(1)
            # Remove old BearID: from new note
            md_text = (
                re.sub(r"\<\!-- ?\{BearID\:" + uuid + r"\} ?--\>", "", md_text).rstrip()
                + "\n"
            )

            sync_conflict = self.check_sync_conflict(uuid, ts_last_export)
            if sync_conflict:
                link_original = "bear://x-callback-url/open-note?id=" + uuid
                message = (
                    "::Sync conflict! External update: " + self.time_stamp_ts(ts) + "::"
                )
                message += (
                    "\n[Click here to see original Bear note](" + link_original + ")"
                )
                x_create = "bear://x-callback-url/create?show_window=no"
                self.bear_x_callback(x_create, md_text, message, "")
            else:
                # Regular external update
                orig_title = self.backup_bear_note(uuid)
                # message = '::External update: ' + time_stamp_ts(ts) + '::'
                x_replace = (
                    "bear://x-callback-url/add-text?show_window=no&mode=replace&id="
                    + uuid
                )
                self.bear_x_callback(x_replace, md_text, "", orig_title)
                # # Trash old original note:
                # x_trash = 'bear://x-callback-url/trash?show_window=no&id=' + uuid
                # subprocess.call(["open", x_trash])
                # time.sleep(.2)
        else:
            # New external md Note, since no Bear uuid found in text:
            # message = '::New external Note - ' + time_stamp_ts(ts) + '::'
            md_text = self.get_tag_from_path(md_text, md_file, export_path)
            x_create = "bear://x-callback-url/create?show_window=no"
            self.bear_x_callback(x_create, md_text, "", "")
        return

    def get_tag_from_path(
        self, md_text, md_file, root_path, inbox_for_root=True, extra_tag=""
    ):
        # extra_tag should be passed as '#tag' or '#space tag#'
        path = md_file.replace(root_path, "")[1:]
        sub_path = os.path.split(path)[0]
        tags = []
        if ".textbundle" in sub_path:
            sub_path = os.path.split(sub_path)[0]
        if sub_path == "":
            if inbox_for_root:
                tag = "#.inbox"
            else:
                tag = ""
        elif sub_path.startswith("_"):
            tag = "#." + sub_path[1:].strip()
        else:
            tag = "#" + sub_path.strip()
        if " " in tag:
            tag += "#"
        if tag != "":
            tags.append(tag)
        if extra_tag != "":
            tags.append(extra_tag)
        for tag in get_file_tags(md_file):
            tag = "#" + tag.strip()
            if " " in tag:
                tag += "#"
            tags.append(tag)
        return md_text.strip() + "\n\n" + " ".join(tags) + "\n"

    def get_file_tags(self, md_file):
        try:
            subprocess.call([self.gettag_sh, md_file, self.gettag_txt])
            text = re.sub(r"\\n\d{1,2}", r"", read_file(self.gettag_txt))
            tag_list = json.loads(text)
            return tag_list
        except:
            return []

    def bear_x_callback(self, x_command, md_text, message, orig_title):
        if message != "":
            lines = md_text.splitlines()
            lines.insert(1, message)
            md_text = "\n".join(lines)
        if orig_title != "":
            lines = md_text.splitlines()
            title = re.sub(r"^#+ ", r"", lines[0])
            if title != orig_title:
                md_text = "\n".join(lines)
            else:
                md_text = "\n".join(lines[1:])
        x_command_text = x_command + "&text=" + urllib.parse.quote(md_text)
        subprocess.call(["open", x_command_text])
        time.sleep(0.2)

    def check_sync_conflict(self, uuid, ts_last_export):
        conflict = False
        # Check modified date of original note in Bear sqlite db!
        with sqlite3.connect(self.bear_db) as conn:
            conn.row_factory = sqlite3.Row
            query = (
                "SELECT * FROM `ZSFNOTE` WHERE `ZTRASHED` LIKE '0' AND `ZUNIQUEIDENTIFIER` LIKE '"
                + uuid
                + "'"
            )
            c = conn.execute(query)
        for row in c:
            modified = row["ZMODIFICATIONDATE"]
            uuid = row["ZUNIQUEIDENTIFIER"]
            mod_dt = dt_conv(modified)
            conflict = mod_dt > ts_last_export
        return conflict

    def backup_bear_note(self, uuid):
        # Get single note from Bear sqlite db!
        with sqlite3.connect(self.bear_db) as conn:
            conn.row_factory = sqlite3.Row
            query = (
                "SELECT * FROM `ZSFNOTE` WHERE `ZUNIQUEIDENTIFIER` LIKE '" + uuid + "'"
            )
            c = conn.execute(query)
        title = ""
        for row in c:  # Will only get one row if uuid is found!
            title = row["ZTITLE"]
            md_text = row["ZTEXT"].rstrip()
            modified = row["ZMODIFICATIONDATE"]
            mod_dt = dt_conv(modified)
            created = row["ZCREATIONDATE"]
            cre_dt = dt_conv(created)
            md_text = self.insert_link_top_note(md_text, "Link to updated note: ", uuid)
            dtdate = datetime.datetime.fromtimestamp(cre_dt)
            filename = self.clean_title(title)  # + dtdate.strftime(' - %Y-%m-%d_%H%M')
            if not os.path.exists(self.sync_backup):
                os.makedirs(self.sync_backup)
            file_part = os.path.join(self.sync_backup, filename)
            # This is a Bear text file, not exactly markdown.
            backup_file = file_part + ".txt"
            count = 2
            while os.path.exists(backup_file):
                # Adding sequence number to identical filenames, preventing overwrite:
                backup_file = file_part + " - " + str(count).zfill(2) + ".txt"
                count += 1
            self.write_file(backup_file, md_text, mod_dt)
            filename2 = os.path.split(backup_file)[1]
            self.write_log("Original to sync_backup: " + filename2)
        return title

    def insert_link_top_note(self, md_text, message, uuid):
        lines = md_text.split("\n")
        title = re.sub(r"^#{1,6} ", r"", lines[0])
        link = (
            "::"
            + message
            + "["
            + title
            + "](bear://x-callback-url/open-note?id="
            + uuid
            + ")::"
        )
        lines.insert(1, link)
        return "\n".join(lines)

    def init_gettag_script(self):
        gettag_script = """#!/bin/bash
        if [[ ! -e $1 ]] ; then
        echo 'file missing or not specified'
        exit 0
        fi
        JSON="$(xattr -p com.apple.metadata:_kMDItemUserTags "$1" | xxd -r -p | plutil -convert json - -o -)"
        echo $JSON > "$2"
        """
        temp = os.path.join(self.HOME, "temp")
        if not os.path.exists(temp):
            os.makedirs(temp)
        self.write_file(self.gettag_sh, gettag_script, 0)
        subprocess.call(["chmod", "777", self.gettag_sh])

    def notify(self, message):
        title = "ul_sync_md.py"
        try:
            # Uses "terminal-notifier", download at:
            # https://github.com/julienXX/terminal-notifier/releases/download/2.0.0/terminal-notifier-2.0.0.zip
            # Only works with MacOS 10.11+
            subprocess.call(
                [
                    "/Applications/terminal-notifier.app/Contents/MacOS/terminal-notifier",
                    "-message",
                    message,
                    "-title",
                    title,
                    "-sound",
                    "default",
                ]
            )
        except:
            write_log('"terminal-notifier.app" is missing!')
        return

