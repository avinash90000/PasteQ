
class clipboardEntry():
    def __init__(self, uuid, text = "", image = "", image_hash = "", widget = "", is_text = True):
        self.uuid = uuid
        self.text = text
        self.image = image
        self.image_hash = image_hash
        self.is_text = is_text
        self.text_to_display = ""
        self.image_to_display = ""
        self.widget = widget
        if self.is_text:
            self.get_text_display()
        else:
            self.get_image_to_display()


    def get_text_display(self):
        text_lines = self.text.count("\n")-1
        if text_lines==1:
            self.text_to_display = self.text.strip().replace("\n", " ")[:25]+"... (+"+str(text_lines)+" line)"
        elif text_lines>0:
            self.text_to_display = self.text.strip().replace("\n", " ")[:25]+"... (+"+str(text_lines)+" lines)"
        else:
            self.text_to_display = self.text.strip().replace("\n", " ")
            if len(self.text_to_display)>35:
                self.text_to_display = self.text_to_display[:32]+"..."


    def get_image_to_display(self):
        self.image_to_display = ""
        