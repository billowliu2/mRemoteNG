using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Versioning;
using mRemoteNG.App;
using mRemoteNG.Messages;
using mRemoteNG.Resources.Language;

namespace mRemoteNG.Connection.Protocol.RDP
{
    [SupportedOSPlatform("windows")]
    public class RdpProtocolFactory
    {
        public RdpProtocol Build(RdpVersion rdpVersion)
        {
            switch (rdpVersion)
            {
                case RdpVersion.Highest:
                    return BuildHighestSupportedVersion();
                case RdpVersion.Rdc6:
                    return new RdpProtocol();
                case RdpVersion.Rdc7:
                    return new RdpProtocol7();
                case RdpVersion.Rdc8:
                    return new RdpProtocol8();
                case RdpVersion.Rdc9:
                    return new RdpProtocol9();
                case RdpVersion.Rdc10:
                    return new RdpProtocol10();
                case RdpVersion.Rdc11:
                    return new RdpProtocol11();
                default:
                    throw new ArgumentOutOfRangeException(nameof(rdpVersion), rdpVersion, null);
            }
        }

        public RdpProtocol BuildWithFallback(RdpVersion requested)
        {
            IEnumerable<RdpVersion> versions = Enum.GetValues(typeof(RdpVersion))
                .OfType<RdpVersion>()
                .Except(new[] { RdpVersion.Highest })
                .Where(version => version <= requested)
                .OrderByDescending(version => version);

            foreach (RdpVersion version in versions)
            {
                RdpProtocol rdp = Build(version);
                if (!rdp.RdpVersionSupported())
                    continue;

                if (version != requested && requested != RdpVersion.Highest)
                {
                    Runtime.MessageCollector.AddMessage(MessageClass.InformationMsg,
                        string.Format(Language.RdpVersionFallback, requested, version));
                }

                return rdp;
            }

            return Build(requested);
        }

        private RdpProtocol BuildHighestSupportedVersion()
        {
            IEnumerable<RdpVersion> versions = Enum.GetValues(typeof(RdpVersion))
                .OfType<RdpVersion>()
                .Except(new[] { RdpVersion.Highest })
                .Reverse();

            foreach (RdpVersion version in versions)
            {
                RdpProtocol rdp = Build(version);
                if (rdp.RdpVersionSupported())
                    return rdp;
            }

            throw new ArgumentOutOfRangeException();
        }

        public List<RdpVersion> GetSupportedVersions()
        {
            IEnumerable<RdpVersion> versions = Enum.GetValues(typeof(RdpVersion))
                .OfType<RdpVersion>()
                .Except(new[] { RdpVersion.Highest });

            List<RdpVersion> supportedVersions = new();
            foreach (RdpVersion version in versions)
            {
                if (Build(version).RdpVersionSupported())
                    supportedVersions.Add(version);
            }

            return supportedVersions;
        }
    }
}
