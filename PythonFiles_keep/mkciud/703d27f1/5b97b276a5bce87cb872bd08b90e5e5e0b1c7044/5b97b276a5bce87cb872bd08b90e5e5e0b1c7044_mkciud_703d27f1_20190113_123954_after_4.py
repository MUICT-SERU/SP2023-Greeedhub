from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import gzip


SUBTYPE_PREFIX_MAP={
    "cloud-boothook":       "#cloud-boothook\n",
    "cloud-config":         "#cloud-config\n",
    "cloud-config-archive": "#cloud-config-archive\n",
    "part-handler":         "#part-handler\n",
    "upstart-job":          "#upstart-job\n",
    "x-include-once-url":   "#include-once\n",
    "x-include-url":        "#include\n",
    "x-shellscript":        "#!",
}


class UserData(object):
    def __init__(self):
        self.multipart_message = MIMEMultipart()

    def add(self, message_body, message_subtype=None):
        if not message_subtype:
            for subtype, prefix in SUBTYPE_PREFIX_MAP.items():
                if message_body.startswith(prefix):
                    message_subtype = subtype
                    break
            if not message_subtype:
                raise RuntimeError("could not determine message subtype")

        # TODO remove unnecessary prefix
        # prefix = SUBTYPE_PREFIX_MAP[message_subtype]
        # if prefix.endswith("\n"):
        #     message_body = message_body[len(prefix):]
        self.multipart_message.attach(MIMEText(message_body, message_subtype))

    def export(self, fileobj):
        with gzip.GzipFile(mode="wb", fileobj=fileobj) as f:
            f.write(self.multipart_message.as_bytes())
