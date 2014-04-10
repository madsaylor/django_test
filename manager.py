
class InLifeUserQuerySet(models.query.QuerySet):
    def with_achievements(self):        
        user_ids = []
        thumbnails = {}
        for user in self.all():
            user_ids.append(user.id)
            if isfile(join(MEDIA_ROOT,str(user.photo))):
                thumb_url = get_thumbnailer(user.photo).get_thumbnail({
                    'size': (100, 100),
                    'box': user.cropping,
                    'crop': True,                
                }).url
                thumbnails[user.id] = thumb_url
            else:
                thumbnails[user.id] = None         
        if not user_ids:
            return 
        cursor = connection.cursor()
        sql= """
                SELECT users_inlifeuser.id, users_inlifeuser.username, users_inlifeuser.first_name, 
                users_inlifeuser.last_name, users_inlifeuser.is_premium, app_achievement.name, 
                app_userachievement.status, app_achievement.icon_color
                FROM app_userachievement  
                INNER JOIN users_inlifeuser  
                ON users_inlifeuser.id = app_userachievement.user_id  
                INNER JOIN app_achievement  
                ON app_userachievement.achievement_id = app_achievement.id 
                WHERE app_userachievement.status IN (2,4)
                AND NOT (users_inlifeuser.first_name = '' OR users_inlifeuser.last_name = '' OR users_inlifeuser.photo = '')                
                AND users_inlifeuser.id IN ({})
            """.format(', '.join([str(i) for i in user_ids]))

        cursor.execute(sql)
        rows = dictfetchall(cursor)
        sliced_rows = []
        for row in rows:
            user_slice = dict((key, row[key]) for key in ('id', 'username', 'first_name', 'last_name', 'is_premium'))                 
            user_slice['thumbnail'] = thumbnails[user_slice['id']]
            sliced_rows.append(user_slice)
        result_list = [dict(t) for t in set([tuple(d.items()) for d in sliced_rows])]
        for sliced_row in result_list:
            achievements = []
            for row in rows:
                if row['id'] == sliced_row['id']: 
                    achievements.append(dict((key, row[key]) for key in ('name', 'status', 'icon_color')))            
            sliced_row['achievements'] = achievements
        return result_list
    
class InLifeUserManager(UserManager):
    def get_query_set(self):
        return InLifeUserQuerySet(self.model)
