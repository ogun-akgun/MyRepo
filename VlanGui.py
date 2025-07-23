#1.4
#Description is created with cluster name instead of tenant name
# V1.3
#1.2 Added L3-VNI support
#1.3 VLAN Vlan Groups slug updates as group name
# Bug in STD labs
# Changed decreption with clustername instead of tenant name (adds CENTRAL/SCx in DC labs)
#Copyright(c) by Ogun Akgun, Windriver
#ogun.akgun@windriver.com
#2025.
import tkinter as tk
from tkinter import ttk
from idlelib.tooltip import Hovertip
from tkinter import StringVar
import ipaddress
import pynetbox
import urllib3
from win32cryptcon import szOID_X957
from win32ui import CreateToolTipCtrl

nb = pynetbox.api('https://yow-netbox.wrs.com', token='')
urllib3.disable_warnings()
nb.http_session.verify = False
#from scipy.stats import false_discovery_control

def radio_click(val: object) -> object:
    print(val)
    try:
        group_name = nb.ipam.vlan_groups.all()
        for grn in group_name:
            if str(grn.scope) == val and grn.name.startswith("VNI-GROUP-"):
                print(f"VLAN GROUP {grn.name} ")
                print(f"VNI is {grn.slug} ")
                #self.found=True
                a = grn.slug
                return a
    except pynetbox.RequestError as e:
        print(f"Error occurred while filtering VLAN groups: {e}")

def main():
    app = Application()
    app.mainloop()


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WindRiver")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=9)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=9)
        self.geometry("1440x960")
        frame = InputForm1(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        #frame2 = InputForm2(self)
        #frame2.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)



class InputForm1(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.r = None
        global text
        self.text="Will get it from Netbox"
        self.columnconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(4, weight=9)
        self.columnconfigure(4, weight=9)
        #v=tk.StringVar()
        #vv=tk.StringVar()
        self.lblTName = ttk.Label(self, text="Tenant Name : ",justify=tk.LEFT)
        self.lblTName.grid(row=0, column=0)
        self.entryTName = ttk.Entry(self, width=30)
        self.entryTName.grid(row=0, column=1, sticky="ew")

        self.lblCName = ttk.Label(self, text="Cluster Name : ",justify=tk.LEFT)
        self.lblCName.grid(row=2, column=0)
        self.entryCName = ttk.Entry(self, width=30,takefocus=True)
        self.entryCName.grid(row=2, column=1, sticky="ew")
        self.clt=tk.StringVar()
        self.cltype = ttk.Combobox(self, textvariable=self.clt, state="readonly")
        self.cltype['values']=('AIO-SX', 'AIO-DX','AIO-STD','AIO-Plus','AIO-STD+STRG')
        self.cltype.grid(row=2, column=2, sticky="ew")
        self.cltype_ttp=Hovertip(self.cltype, "Choose Cluster Type\n If you are using a cluster from a DC Lab")
        self.cltype.current(0)
        self.lblVNI = ttk.Label(self, text="VNI Prefix : ",justify=tk.LEFT)
        self.lblVNI.grid(row=3, column=0)



        self.entryVNI = ttk.Label(self, width=30,text=self.text)

        self.entryVNI.grid(row=3, column=1, sticky="ew")
        self.radio_var=tk.StringVar(value="YOW 425 LEGGET")
        self.radio=ttk.Radiobutton(self, text="LEGGET",variable=self.radio_var, value="YOW 425 Legget",command=self.on_radio_select)
        self.radio.grid(row=3, column=2, sticky="ew")
        self.radio2=ttk.Radiobutton(self, text="COLO",variable=self.radio_var, value="YOW2 COLO",command=self.on_radio_select)
        self.radio2.grid(row=3, column=3, sticky="ew")
        self.chkd = tk.BooleanVar()
        self.chkd.set(False)  # Default unchecked

        self.checkbutton = ttk.Checkbutton(self, text="DataVlan >50",variable=self.chkd,command=self.print_Vlans)
        self.checkbutton.grid(row=3, column=4, sticky="ew")
        self.genVlan=ttk.Button(self,text="Generate Vlan",command=self.print_Vlans,state=tk.DISABLED)
        self.genVlan.grid(row=2, column=4, sticky="w")
        self.updVlan = ttk.Button(self, text="Update Netbox",command=self.update_netbox,state=tk.DISABLED)
        self.updVlan_ttp=Hovertip(self.updVlan, "This updates all the data to Netbox.\n Make sure that all information is accurate.")
        self.updVlan.grid(row=0, column=4, sticky="w")
        self.result_text = tk.Text(self)
        self.result_text.grid(row=4, column=0, columnspan=9, sticky="nsew",ipadx=450, ipady=450)
        #self.result_text.pack(ipadx=100, ipady=15, fill="both", expand=True)

    def chkbx(val):
        print(val)
        val.generate_Vlan(self)
    def on_radio_select(self):
        print(f"Selected option: {self.radio_var.get()}")
        self.genVlan.configure(state=tk.NORMAL)
        self.r=str(radio_click(self.radio_var.get()))
        self.text=self.r
        self.entryVNI.config(text=self.text)
        print(self.text)

        #text=tk.StringVar(chkbx(self.chkd.get()))
        #self.entryVNI=ttk.Entry(self, textvariable=text)
        #self.entryVNI.pack()
    def generate_Vlan(self,*args) -> None:
        self.genVlan.configure(state=tk.NORMAL)
        #self.r = str(radio_click(self.radio_var.get()))  #This function reruns
        self.text = self.r
        self.entryVNI.config(text=self.text)
        self.updVlan.configure(state=tk.NORMAL)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        tenant_name = self.entryTName.get().upper()
        cluster_name = self.entryCName.get().upper()
        cluster_name_lower = self.entryCName.get().lower()
        location=self.radio_var.get()
        prefix = int(self.text[-4:])
        if location == "YOW 425 Legget":
            prefix = prefix - 639
            if self.chkd.get():
                A = 40
                B = 100
                vlans=50
            else:
                A = 40
                B = 65
                vlans=10
        else:
            if self.chkd.get():
                A = 15
                B = 75
                vlans=50
            else:
                A = 15
                B = 40
                vlans=10
        print("\n\n")
        print("vid,cf_VNI,tenant,group,name,location,status,role,description,tags")
        self.result_text.insert(tk.END, "vid,cf_VNI,tenant,group,name,location,status,role,description,tags\n")
        for i in range(A, B):
            # Define common variables

            # Determine specific parts of the output based on the current number
            if i == A:
                role, suffix, status, description, tags = "PXE", "pxe", "active", "PXE", "pxe-network"
            elif i == A + 1:
                role, suffix, status, description, tags = "MGMT", "mgmt", "active", "MGMT", "mgmt-network"
            elif i == A + 2:
                role, suffix, status, description, tags = "CLUSTER", "cluster", "active", "CLUSTER", "cluster-network"
            elif i == A + 3:
                if "CENTRAL" in cluster_name :
                    role, suffix, status, description, tags = "ADMIN", "admin", "reserved", "ADMIN-0", "admin-network"
                else:
                    role, suffix, status, description, tags = "ADMIN", "admin", "active", "ADMIN-0", "admin-network"
            elif i == A + 4:
                role, suffix, status, description, tags = "ADMIN1", "admin", "reserved", "Reserved for ADMIN-1", "admin-network"
            elif i == A + 5:
                role, suffix, status, description, tags = "SharedSRIOV", "sharedsriov", "reserved", "Reserved for SRIOV-0", "sharedsriov"
            elif i == A + 6:
                role, suffix, status, description, tags = "SRIOV", "sriov", "reserved", "Reserved for SRIOV-1", "sharedsriov"
            elif i == A + 7:
                role, suffix, status, description, tags = "STORAGE-0", "storage", "reserved", "Reserved for STORAGE-0", "storage-0"
            elif i == A + 8:
                role, suffix, status, description, tags = "STORAGE-1", "storage", "reserved", "Reserved for STORAGE-1", "storage-1"
            elif i == A + 9:
                role, suffix, status, description, tags = "", f"future-use", "reserved", "Reserved for future use", ""
            elif A + 10 <= i < A + vlans + 5:
                role, suffix, status, description, tags = "DATA-0", "data", "active", "DATA", "data-network"
            elif A + 10 <= i < A + vlans + 10:
                if not self.chkd.get():
                    role, suffix, status, description, tags = "DATA-0", "data", "reserved", "DATA", "data-network"
            else:
                role, suffix, status, description, tags = "", f"future-use", "reserved", "Reserved for future use", ""

            print(
                f"{i},{prefix}{i},{tenant_name},{cluster_name},{location},{cluster_name_lower}-{suffix}-{i},{status},{role},{cluster_name} {description},{tags}")
            self.result_text.insert(tk.END, f"{i},{prefix}{i},{tenant_name},{cluster_name},{location},{cluster_name_lower}-{suffix}-{i},{status},{role},{cluster_name} {description},{tags}\n")
            for ar in args:
                if ar=="y":
                    self.add_vlan(str(i),str(prefix) + str(i),tenant_name,cluster_name,location,cluster_name_lower + "-" + suffix + "-" + str(i),status,cluster_name + " " + description,role,tags)

        for ar in args:
            if ar=="y":
                print("Generate Vlans")
            elif ar=="n":
                self.result_text.insert(tk.END," ---------------------------------------------------------------\n                       !!WARNING!!\n ---------------------------------------------------------------\n  **** If you want to do manual import proceed following steps first..****\n")
                self.result_text.insert(tk.END,
                                    f"1-Make sure that tenant {tenant_name} exists, don't forget to add {cluster_name} as cluster and cluster group to \n  Tenant {tenant_name} in Netbox Tenant: Virtualization > Clusters\n")
                self.result_text.insert(tk.END,
                                    f"2-Don't forget to rename Vlan Group {self.text.upper()} to {cluster_name} in Netbox Cluster > VLAN Groups\n")
                if vlans>10 and location == "YOW 425 Legget":
                    nprefix=str(prefix+1278).zfill(4)
                    self.ntext="VNI-GROUP-"+nprefix
                    self.result_text.insert(tk.END,
                                    f"3-You need to delete Vlan Group {self.ntext} int Netbox IPAM > VLAN Groups\n")
                    self.result_text.insert(tk.END,
                                    f"4-You need to update Spreadsheet  https://windriversystems.sharepoint.com/:x:/r/sites/EngineeringSharedServices/Internal/_layouts/15/doc2.aspx?sourcedoc=%7BF585BD39-6B13-42FF-9AD7-46E2C9574E24%7D&file=VNI%20ID%20GROUPs.xlsx&action=default&mobileredirect=true \n")
        #print("Generate Vlans")
    def on_checkbutton_toggle(self):
        print(f"Checkbutton toggled: {self.chkd.get()}")
    def print_Vlans(self):
        result=self.generate_Vlan(self,"n")
    def add_vlan(self,vid,vni,tenant,group,site,name,status,description,role=None,tags=None):
        tenantid=int(nb.tenancy.tenants.get(slug=tenant.lower()).id)
        groupid=int(nb.ipam.vlan_groups.get(name=group.upper()).id)
        siteid=int(nb.dcim.sites.get(name=site).id)
        if role=='':
            roleid=1
        else:
            roleid=int(nb.ipam.roles.get(name=role).id)
        tagsid=[nb.extras.tags.get(slug=tags.lower()).id for tag in tags] if tags else []

        try:
            # Create VLAN data dictionary

            vlan_data = {
                "vid": vid,
                "custom_fields":{'VNI':int(vni)},
                "tenant": tenantid,
                "group": groupid,
                "site": siteid,
                "name": name,
                "status": status,
                "role": roleid,
                "description": description,
                "tags": tagsid
            }
            if role=='':
                vlan_data.pop("role")
            # Create the VLAN
            vlan = nb.ipam.vlans.create(vlan_data)
            #vlan = nb.ipam.vlans.create(name=name, vid=vid, tenant=tenantid, group=groupid, site=siteid, custom_fields={'VNI':int(vni)}, status=status, description=description, tags=tagsid)
            print(vlan_data)
            if vlan:
                self.result_text.insert(tk.END,f"Successfully created VLAN: {name} (ID: {vid})")
                #print(f"Successfully created VLAN: {name} (ID: {vid})")
            else:
                print("Failed to create VLAN")
        except pynetbox.RequestError as e:
            print(f"Error adding VLAN: {e}")
    def rename_vlan_group(self):
       # a= self.onClick()
        print("Renaming VLAN Group")
        try:
            vlan_group = nb.ipam.vlan_groups.get(slug=self.text)
            if vlan_group:
                vlname = str(self.entryCName.get().upper())
                update_data = {
                    "name": vlname,
                    "slug": vlname.lower().replace(" ","-")
                }
                vlan_group.update(update_data)
                print(f"VLAN group '{self.text}' renamed to '{vlname}'")
                return True
        except pynetbox.RequestError as e:
            print(f"Error occurred while filtering VLAN groups: {e}")
            return False
    def update_netbox(self):
        TN=str(self.entryTName.get().upper())
        CN=self.entryCName.get().upper()
        result=self.get_or_create_tenant(TN)
        if result:
            result1=self.get_or_create_cluster_group(CN)
            if result1:
                result2=self.get_or_create_cluster(str(CN),TN,self.radio_var.get())

        result=self.rename_vlan_group()
        if self.chkd.get():
            result3=self.modify_vlan_info()
            if result3:
                print("Vlan info modified")
               # result4=self.generate_Vlan(self,"y")
               # if result4:
               #     print("Vlan info generated")

        if result:
            self.generate_Vlan(self,"y")
    def get_or_create_tenant(self,tn):
        """
           Check if the tenant exists in NetBox. If not, create it.

           Args:
               tenant_name (str): The name of the tenant.
               tenant_slug (str): The slug for the tenant (optional, derived from name if not provided).
               tenant_description (str): Description of the tenant (default is empty).

           Returns:
               tenant (object): The tenant object from NetBox.
           """
        # Convert name to lowercase slug-style if no slug is provided
        tenant_slug = tn.lower()

        # Check if the tenant exists
        tenant = nb.tenancy.tenants.get(slug=tenant_slug)
        if tenant:
            print(f"Tenant '{tn}' already exists.")
            return True  # Return the existing tenant

        # Tenant does not exist, create it
        try:
            tenants = nb.tenancy.tenants.all()
            l3_vni_list = [tenant.custom_fields['L3_VNI'] for tenant in tenants if tenant.custom_fields['L3_VNI'] != None]
            sorted_l3_vn_is = sorted(l3_vni_list)
            first_available_l3_vni = (sorted_l3_vn_is[-1]) + 1
            group_name=self.cltype.get().upper()
            group_name=group_name.replace("AIO-","WRCP - ")
            group = nb.tenancy.tenant_groups.get(name=group_name).id
            #tags=0
            #tags=nb.extras.tags.get(slug=self.cltype.get().lower()).id
            #tags=tags.append(int(nb.extras.tags.get(Slug="yow").id))
            new_tenant_data = {
                "name": tn,
                "slug": tenant_slug,
                "description": tn,
                "custom_fields": {'L3_VNI':first_available_l3_vni},
                "group": group

            }
            tenant = nb.tenancy.tenants.create(new_tenant_data)  # Create the tenant
            print(f"Tenant '{tn}' has been created successfully.")
            return True
        except pynetbox.RequestError as e:
            print(f"Error creating tenant: {e}")
            return None
    def get_or_create_cluster_group(self,group_name):
        """
        Check if the cluster group exists in NetBox. If not, create it.

        Args:
            group_name (str): The name of the cluster group.
            slug (str): The slug for the cluster group (optional, derived from name if not provided).
            description (str): Optional description of the cluster group.

        Returns:
            group (object): The cluster group object from NetBox.
        """
        # Generate slug from name if not provided
        slug = group_name.lower()
        slug1=slug.replace(" ","-")
        try:
            # Check if the cluster group exists
            group = nb.virtualization.cluster_groups.get(slug=slug1)
            if group:
                print(f"Cluster group '{group_name}' already exists.")
                return True

            # Create the cluster group if it doesn't exist
            new_group_data = {
                "name": group_name,
                "slug": slug1,
                "description": group_name,
            }
            group = nb.virtualization.cluster_groups.create(new_group_data)
            if group:
                print(f"Cluster group '{group_name}' has been created successfully.")
            return True

        except pynetbox.RequestError as e:
            print(f"Error occurred while checking or creating cluster group: {e}")
            return None
    def get_or_create_cluster(self,cluster,tenant,site):
        """
        Check if a cluster exists in NetBox. If not, create it.

        Args:
            cluster_name (str): The name of the cluster.
            group (str): The name of the cluster group (optional).
            tenant (str): The tenant name associated with the cluster (optional).
            site (str): Site name associated with the cluster (optional).
            description (str): Optional description of the cluster.

        Returns:
            cluster (object): The cluster object from NetBox.
        """
        try:
            # Check if the cluster already exists
            cluster1 = nb.virtualization.clusters.get(name=cluster)
            if cluster1:
                print(f"Cluster '{cluster1}' already exists.")
                return True

            # Retrieve cluster group, tenant, or site, if provided
            tags=[]
            type_obj = ""
            site_obj = site
            if 'SX' in str(cluster):
                type_obj = 'wrcp-aio-sx'
                tags.append(int(nb.extras.tags.get(slug="aio-sx").id))

            if 'DX' in str(cluster):
                type_obj = 'wrcp-aio-dx'
                tags.append(int(nb.extras.tags.get(slug="aio-dx").id))

            if 'STD' in str(cluster):
                type_obj = 'wrcp-aio-std'
                tags.append(int(nb.extras.tags.get(slug="standard-with-dedicated-storage-cluster").id))
            if 'DC' in str(cluster):

                type_obj='wrcp'+'-'+self.cltype.get().lower()
                if 'CENTRAL' in str(cluster):
                    tags.append(int(nb.extras.tags.get(slug="central-controllers").id))
                    tags.append(int(nb.extras.tags.get(slug=self.cltype.get().lower()).id))

                if 'SC' in str(cluster):
                    index=cluster.find("SC")
                    tags.append(int(nb.extras.tags.get(slug="dc-sub-cloud").id))
                    ss=cluster[index:]
                    a=ss.rstrip('0123456789')
                    b=ss[len(a):]
                    sonuc=a+'-'+b[:2].rjust(2,'0')
                    tags.append(int(nb.extras.tags.get(slug=sonuc.lower()).id))
                    tags.append(int(nb.extras.tags.get(slug=self.cltype.get().lower()).id))

            cluster1=cluster.replace(" ","-")
            cluster_group_id=int(nb.virtualization.cluster_groups.get(slug=cluster1.lower()).id)
            #cluster_group_id=int(nb.virtualization.cluster_groups.get(slug=cluster.lower()).id)
            tenant_id=int(nb.tenancy.tenants.get(slug=tenant.lower()).id)
            site_id=int(nb.dcim.sites.get(name=site_obj).id)
            typeid=int(nb.virtualization.cluster_types.get(slug=type_obj).id)
            new_cluster_data = {
                "name": cluster,
                "group": cluster_group_id,
                "tenant": tenant_id,
                "site": site_id,
                "description": cluster or "",
                "status": "active",
                "type": typeid,
                "tags": tags
            }

            # Remove keys with `None` values
            new_cluster_data = {k: v for k, v in new_cluster_data.items() if v is not None}

            # Create the cluster
            cluster = nb.virtualization.clusters.create(new_cluster_data)
            if cluster:
                print(f"Cluster '{cluster}' has been created successfully.")
                return True

        except pynetbox.RequestError as e:
            print(f"Error occurred while checking or creating cluster: {e}")
            return None
    def modify_vlan_info(self):
        print("Modifying VLANs")
        try:
            vlan_group = nb.ipam.vlan_groups.get(slug=self.text)
            if vlan_group:
                vlname = str(self.entryCName.get().upper())
                update_data = {
                    "name": vlname,
                    "max_vid": 99,
                    "slug": vlname.lower()
                }
                vlan_group.update(update_data)
                print(f"VLAN group '{self.text}' renamed to '{vlname}'")
                a =self.text.rstrip('0123456789')
                b=self.text[len(a):]
                ab =639+int(b.rjust(4,'0'))
                deletedgroup='vni-group-'+str(ab).zfill(4)
                vlan_group_deleted=nb.ipam.vlan_groups.get(slug=deletedgroup)
                if vlan_group_deleted:
                    update_data1 = {
                        "name": 'DELETED !! '+ deletedgroup,
                        "description": 'DELETED !! Due to Expansion of '+vlname
                    }
                    vlan_group_deleted.update(update_data1)
                    print(f"VLAN group '{deletedgroup}' deleted")
                return True
        except pynetbox.RequestError as e:
            print(f"Error occurred while checking or creating cluster: {e}")
            return None


if __name__ == "__main__":
    main()