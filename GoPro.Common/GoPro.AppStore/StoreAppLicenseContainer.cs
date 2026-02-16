using System.Collections.Generic;
using Windows.Services.Store;

namespace GoPro.AppStore
{
	public class StoreAppLicenseContainer
	{
		public IReadOnlyDictionary<string, StoreAddOnLicenseContainer> AddOnLicenses { get; }

		public StoreAppLicenseContainer(IReadOnlyDictionary<string, StoreAddOnLicenseContainer> addOnLicenses)
		{
			AddOnLicenses = addOnLicenses;
		}

		public StoreAppLicenseContainer(StoreAppLicense appLicense)
		{
			Dictionary<string, StoreAddOnLicenseContainer> dictionary = new Dictionary<string, StoreAddOnLicenseContainer>();
			foreach (StoreLicense value in appLicense.get_AddOnLicenses().Values)
			{
				dictionary.Add(AddOnLicense.ExtractStoreIdFromExtendedJsonData(value.get_ExtendedJsonData()), new StoreAddOnLicenseContainer(value));
			}
			AddOnLicenses = dictionary;
		}
	}
}
