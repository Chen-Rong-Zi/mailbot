class Applicant():
    def __init__(self, user_data, results=None):
        self.user_data = user_data
        self.results   = results

    def set_materials_done(self, base):
        """
        base: to set that this applicant's resources have been fetched
        """
        pass

    def is_materials_done(self):
        """
        是否获取了相关材料。
        """

    def had_send_mail(self, base):
        """
        base: to query whether this applicant's mail had been sent
        """
    
    def preview(self):
        pass
