using System.Windows.Data;

namespace GoPro.Instance
{
	public class LocalizationExtension : Binding
	{
		public LocalizationExtension(string name)
			: base("[" + name + "]")
		{
			((Binding)this).set_Mode((BindingMode)1);
			((Binding)this).set_Source((object)LocalizationService.Instance);
		}

		public LocalizationExtension()
			: base("[]")
		{
			((Binding)this).set_Mode((BindingMode)1);
			((Binding)this).set_Source((object)LocalizationService.Instance);
		}
	}
}
