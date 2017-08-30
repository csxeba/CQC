import sqlite3 as sql

from util.const import DBPATH, METAPATH


def read_meta(path):
    try:
        with open(path) as fileobj:
            data = fileobj.read()
    except FileNotFoundError:
        print("MetaHandler: no metadata file :(")
        return {}
    lines = data.split("\n")
    mapping = {
        k.strip(): v.strip() for k, v in
        [line.split(":") for line in lines if line]
    }
    return mapping


class DBConnection:
    """
    Modszer -E Parameter -E Kontroll_diagram -E Kontroll_meres
    """

    conn = sql.connect(DBPATH)
    c = conn.cursor()
    x = c.execute
    meta = read_meta(METAPATH)
    _currentuser = None

    def current_user(self, gettasz=False):
        if self._currentuser is None:
            import getpass
            tasz = getpass.getuser()
            if not tasz.isdigit():
                tasz = "315855"
            self.x("SELECT * FROM Staff WHERE tasz == ?;", [tasz])
            self._currentuser = self.c.fetchone()
        return self._currentuser[int(not gettasz)]

    def get_username(self, tasz, alias=0):
        col = ["name", "alias1", "alias2"]
        got = self.query(f"SELECT {col[alias]} FROM Staff WHERE tasz == ?;", [tasz])
        return got[0][0] if got else ""

    def get_tasz(self, name):
        self.x("SELECT tasz FROM Staff WHERE name == ? OR alias1 == ? OR alias2 == ?;",
               [name] * 3)
        results = self.c.fetchall()
        if len(results) > 1:
            print(f"Multiple TASZ values for NAME: {name} - {', '.join(r[0] for r in results)}")
        return results[0][0]

    def query(self, select, args=()):
        self.x(select, args)
        return list(self.c.fetchall())

    def insert(self, recobj):
        keys, values = list(zip(*[[key, val] for key, val in recobj.data if val is not None]))
        N = len(keys)
        sqlcmd = f"INSERT INTO {recobj.table} ({','.join(keys)}) " + \
                 f"VALUES ({','.join('?' for _ in range(N))});"
        print("Running insert:", sqlcmd)
        # with self.conn:
        #     self.x(sqlcmd, values)

    def new_cc(self, ccobj):
        for stage in ccobj.stages[::-1]:
            self.insert(ccobj.rec[stage])
            print("Saved", stage)
            if stage == ccobj.unsaved:
                break

    def delete_cc(self, ccID):
        delete_data = "DELETE * FROM Kontroll_meres WHERE cc_id == ?;"
        delete_cc = "DELETE * FROM Kontroll_diagram WHERE id == ?;"
        with self.conn:
            self.x(delete_data, [ccID])
            self.x(delete_cc, [ccID])

    def update_cc(self, ccobj):
        ccr = ccobj.ccrec
        update = " ".join((
            "UPDATE Control_chart SET ",
            ", ".join(f"{f} = ?" for f in ccr.fields[1:]),
            "WHERE id = ?"
        ))
        vals = [ccobj.ccrec[f] for f in ccr.fields[1:] + ("id",)]
        vals[-4:-1] = map(float, vals[-4:-1])
        with self.conn:
            self.x(update, vals)

    def add_measurements(self, cc_ID, dates, points):
        insert = "INSERT INTO Kontroll_meres VALUES (?,?,?)"
        with self.conn:
            self.conn.executemany(insert, ((cc_ID, d, p) for d, p in zip(dates, points)))

    def delete_measurements(self, cc_ID):
        delete = "DELETE * FROM Kontroll_meres WHERE cc_id == ?;"
        with self.conn:
            self.x(delete, cc_ID)

    def modify_measurements(self, cc_ID, dates, points):
        self.delete_measurements(cc_ID)
        self.add_measurements(cc_ID, dates, points)
