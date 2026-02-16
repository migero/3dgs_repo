using System;
using System.Management;

namespace GoPro.Utils
{
	public class VideoController
	{
		private string mName;

		private string mDescription;

		private string mVendorName;

		private string mSimplifiedVendorName;

		private string mDeviceName;

		private string mStatus;

		private string mVendorIdHex;

		private string mDeviceIdHex;

		private string mCurrentDriverVersionString;

		private DateTime mCurrentDriverDate;

		private string mLatestDriverVersionString;

		private string mLatestDriverDateString;

		private string mDriverDownloadURL;

		public string Name => mName;

		public string Description => mDescription;

		public string VendorName => mVendorName;

		public string SimplifiedVendorName => mSimplifiedVendorName;

		public string DeviceName => mDeviceName;

		public string Status => mStatus;

		public string VendorIdHex => mVendorIdHex;

		public uint VendorId => Convert.ToUInt32(mVendorIdHex, 16);

		public string DeviceIdHex => mDeviceIdHex;

		public ulong DeviceId => Convert.ToUInt64(mDeviceIdHex, 16);

		public string PnpID => $"{mVendorIdHex}:{mDeviceIdHex}";

		public string CurrentDriverVersionString => mCurrentDriverVersionString;

		public DateTime CurrentDriverDate => mCurrentDriverDate;

		public string LatestDriverVersionString => mLatestDriverVersionString;

		public string LatestDriverDateString => mLatestDriverDateString;

		public string DriverDownloadURL => mDriverDownloadURL;

		public VideoController(ManagementObject obj)
		{
			if (obj == null)
			{
				return;
			}
			mName = SystemInfoHelper.ConvertManagementObjectValueToString(((ManagementBaseObject)obj).get_Item("Name"), allowNull: false);
			mDescription = SystemInfoHelper.ConvertManagementObjectValueToString(((ManagementBaseObject)obj).get_Item("Description"), allowNull: false);
			mVendorName = SystemInfoHelper.ConvertManagementObjectValueToString(((ManagementBaseObject)obj).get_Item("AdapterCompatibility"), allowNull: false);
			mSimplifiedVendorName = GetSimplifiedVendorName(mVendorName);
			mDeviceName = SystemInfoHelper.ConvertManagementObjectValueToString(((ManagementBaseObject)obj).get_Item("VideoProcessor"), allowNull: false);
			mCurrentDriverVersionString = SystemInfoHelper.ConvertManagementObjectValueToString(((ManagementBaseObject)obj).get_Item("DriverVersion"), allowNull: false);
			mStatus = SystemInfoHelper.ConvertManagementObjectValueToString(((ManagementBaseObject)obj).get_Item("Status"), allowNull: false);
			string text = SystemInfoHelper.ConvertManagementObjectValueToString(((ManagementBaseObject)obj).get_Item("PNPDeviceID"), allowNull: false);
			if (text != null)
			{
				int num = text.IndexOf("VEN_");
				int num2 = text.IndexOf("DEV_");
				if (num >= 0 && text.Length >= num + 8)
				{
					mVendorIdHex = text.Substring(num + 4, 4);
				}
				if (num2 >= 0 && text.Length >= num2 + 8)
				{
					mDeviceIdHex = text.Substring(num2 + 4, 4);
				}
			}
			try
			{
				string text2 = SystemInfoHelper.ConvertManagementObjectValueToString(((ManagementBaseObject)obj).get_Item("DriverDate"), allowNull: false);
				if (text2 != null)
				{
					mCurrentDriverDate = ManagementDateTimeConverter.ToDateTime(text2).ToUniversalTime();
				}
			}
			catch
			{
			}
		}

		public string GetSimplifiedVendorName(string fullname)
		{
			if (string.IsNullOrEmpty(fullname))
			{
				fullname = mName;
			}
			if (fullname.Equals("NVIDIA", StringComparison.OrdinalIgnoreCase) || fullname.ToUpper().Contains("NVIDIA"))
			{
				return "NVIDIA";
			}
			if (fullname.ToUpper().Contains("AMD") || fullname.ToUpper().Contains("Advanced Micro Devices".ToUpper()))
			{
				return "AMD";
			}
			if (fullname.Equals("Intel Corporation", StringComparison.OrdinalIgnoreCase) || fullname.ToUpper().Contains("INTEL"))
			{
				return "Intel";
			}
			return "Other";
		}

		public void QueryLatestDriverVersion(AvailableGraphicsDrivers drivers)
		{
			if (drivers == null || drivers.Devices == null || drivers.Vendors == null)
			{
				return;
			}
			foreach (GraphicsVendorInfo vendor in drivers.Vendors)
			{
				if (VendorIdHex == vendor.VendorID)
				{
					mDriverDownloadURL = vendor.DriverURL;
					break;
				}
			}
			if (drivers.Devices.TryGetValue(PnpID, out var value))
			{
				mLatestDriverVersionString = value.DriverVersion;
				mLatestDriverDateString = value.DriverDate;
			}
		}

		public bool UpdateAvailable()
		{
			if (mLatestDriverVersionString == null || mCurrentDriverVersionString == null)
			{
				return false;
			}
			string[] array = mCurrentDriverVersionString.Split(new char[1] { '.' });
			string[] array2 = mLatestDriverVersionString.Split(new char[1] { '.' });
			if (array.Length == array2.Length && array.Length != 0)
			{
				for (int i = 0; i < array.Length; i++)
				{
					if (int.TryParse(array2[i], out var result) && int.TryParse(array[i], out var result2) && result != result2)
					{
						if (result < result2)
						{
							return false;
						}
						if (result > result2)
						{
							return true;
						}
					}
				}
				return false;
			}
			_ = mCurrentDriverDate;
			if (DateTime.TryParse(mLatestDriverDateString, out var result3))
			{
				return result3 > mCurrentDriverDate;
			}
			return mLatestDriverVersionString.CompareTo(mCurrentDriverVersionString) > 0;
		}
	}
}
